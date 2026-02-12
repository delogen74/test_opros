from django.db import transaction
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Question, Survey, Answer
from .serializers import SubmitSurveySerializer, SurveyPublicSerializer
from .throttling import SurveySubmitRateThrottle

from django.utils.dateparse import parse_date
from django.shortcuts import render, get_object_or_404

from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required


class CustomLoginView(LoginView):
    template_name = "auth/login.html"

    def get_success_url(self):
        user = self.request.user

        if user.is_superuser:
            return "/admin/"

        if hasattr(user, "ownerprofile"):
            return "/dashboard/"

        return "/"


def custom_login_view(request):
    error = None

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            if user.is_superuser:
                return redirect("/admin/")
            else:
                return redirect("/dashboard/")
        else:
            error = "Неверный логин или пароль"

    return render(request, "auth/login.html", {"error": error})


# =====================================================
# HEALTH CHECK
# =====================================================

class HealthView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        return Response({"status": "ok"})


# =====================================================
# ВОПРОСЫ БЕЗ ДУБЛЕЙ
# =====================================================

def get_survey_questions(survey):
    qs = Question.objects.filter(is_active=True)

    categories = []

    if survey.was_pickup:
        categories.append(Question.Category.PICKUP)

    if survey.was_tire_service:
        categories.append(Question.Category.TIRE_SERVICE)

    categories.append(Question.Category.COMMON)

    return (
        qs.filter(category__in=categories)
        .distinct()
        .order_by("order", "id")
    )


# =====================================================
# PUBLIC SURVEY DETAIL
# =====================================================

class PublicSurveyDetailView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, token):
        survey = get_object_or_404(
            Survey.objects.select_related("point"),
            token=token,
        )

        questions = get_survey_questions(survey)

        serializer = SurveyPublicSerializer(
            survey,
            context={"questions": questions},
        )

        return Response(serializer.data)


# =====================================================
# PUBLIC SURVEY SUBMIT
# =====================================================

class PublicSurveySubmitView(APIView):
    authentication_classes = []
    permission_classes = []
    throttle_classes = [SurveySubmitRateThrottle]

    @transaction.atomic
    def post(self, request, token):
        survey = get_object_or_404(
            Survey.objects.select_related("point"),
            token=token,
        )

        if survey.completed:
            return Response(
                {"detail": "Survey already completed."},
                status=status.HTTP_409_CONFLICT,
            )

        questions = get_survey_questions(survey)

        serializer = SubmitSurveySerializer(
            data=request.data,
            context={
                "survey": survey,
                "questions": questions,
            },
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        survey.completed = True
        survey.completed_at = timezone.now()
        survey.save(update_fields=["completed", "completed_at"])

        rating_answers = (
            survey.answers
            .exclude(answer_rating__isnull=True)
            .values_list("answer_rating", flat=True)
        )

        all_ratings_good = bool(rating_answers) and all(r >= 4 for r in rating_answers)

        response_data = {
            "show_review_page": all_ratings_good,
            "review_links": None,
            "average_rating": survey.average_rating,
        }

        if all_ratings_good:
            response_data["review_links"] = {
                "2gis": survey.point.review_link_2gis,
                "yandex": survey.point.review_link_yandex,
            }

        return Response(response_data, status=status.HTTP_200_OK)


# =====================================================
# OWNER DASHBOARD
# =====================================================

@login_required
def owner_dashboard_view(request):

    if request.user.is_superuser:
        return redirect("/admin/")

    if not hasattr(request.user, "ownerprofile"):
        return redirect("login")

    points = request.user.ownerprofile.points.all()

    surveys = Survey.objects.filter(point__in=points).select_related("point")

    date_from = request.GET.get("date_from")
    date_to = request.GET.get("date_to")

    if date_from:
        surveys = surveys.filter(created_at__date__gte=date_from)

    if date_to:
        surveys = surveys.filter(created_at__date__lte=date_to)

    answers = Answer.objects.filter(
        survey__in=surveys,
        answer_rating__isnull=False
    )

    # ==========================
    # ОБЩАЯ СТАТИСТИКА
    # ==========================

    total_orders = surveys.count()
    total_feedback_orders = surveys.filter(completed=True).count()
    total_reviews = answers.count()

    avg_rating = answers.aggregate(avg=Avg("answer_rating"))["avg"]

    # ==========================
    # СТАТИСТИКА ПО КАЖДОМУ ПВЗ
    # ==========================

    point_stats = (
        answers.values(
            "survey__point__id",
            "survey__point__city",
            "survey__point__name",
        )
        .annotate(
            avg_rating=Avg("answer_rating"),
            total_orders_with_rating=Count("survey", distinct=True),
        )
        .order_by("-avg_rating")
    )

    context = {
        "surveys": surveys.order_by("-created_at"),
        "total_orders": total_orders,
        "total_feedback_orders": total_feedback_orders,
        "total_reviews": total_reviews,
        "avg_rating": avg_rating,
        "point_stats": point_stats,
    }

    return render(request, "owner/dashboard.html", context)


# =====================================================
# OWNER SURVEY DETAIL
# =====================================================

@login_required
def owner_survey_detail(request, pk):

    if not hasattr(request.user, "ownerprofile"):
        return render(request, "owner/no_access.html")

    survey = get_object_or_404(
        Survey.objects.select_related("point"),
        pk=pk,
        point__in=request.user.ownerprofile.points.all()
    )

    answers = survey.answers.select_related("question")

    return render(request, "owner/survey_detail.html", {
        "survey": survey,
        "answers": answers
    })

from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect


def custom_login_view(request):
    error = None

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            if user.is_superuser:
                return redirect("/admin/")
            else:
                return redirect("/dashboard/")
        else:
            error = "Неверный логин или пароль"

    return render(request, "auth/login.html", {"error": error})


def custom_logout_view(request):
    logout(request)
    return redirect("login")

