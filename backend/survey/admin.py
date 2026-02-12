from django.contrib import admin
from django.urls import path, reverse
from django.template.response import TemplateResponse
from django.db.models import Avg, Count
from django.shortcuts import get_object_or_404
from django.http import HttpResponseForbidden
from django.utils.html import format_html

from unfold.admin import ModelAdmin

from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

from .models import Survey, Question, Answer, Point, OwnerProfile


# =========================
# POINT
# =========================

@admin.register(Point)
class PointAdmin(ModelAdmin):
    list_display = ("id", "name", "city", "is_active")

    def has_module_permission(self, request):
        return request.user.is_superuser


# =========================
# QUESTION
# =========================

@admin.register(Question)
class QuestionAdmin(ModelAdmin):
    list_display = (
        "id",
        "text",
        "category",
        "type",
        "is_active",
        "is_required",
        "order",
    )
    ordering = ("order", "id")

    def has_module_permission(self, request):
        return request.user.is_superuser


# =========================
# ANSWER INLINE
# =========================

class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0
    readonly_fields = (
        "question",
        "answer_rating",
        "answer_yes_no",
        "answer_text",
        "created_at",
    )
    can_delete = False


# =========================
# SURVEY
# =========================

@admin.register(Survey)
class SurveyAdmin(ModelAdmin):

    list_display = (
        "id",
        "order_number",
        "point",
        "average_rating",
        "completed",
        "created_at",
        "view_link",
    )

    ordering = ("-created_at",)
    inlines = [AnswerInline]

    # ===== ДОСТУП =====

    def has_module_permission(self, request):
        return request.user.is_superuser or hasattr(request.user, "ownerprofile")

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser or hasattr(request.user, "ownerprofile")

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser or hasattr(request.user, "ownerprofile")

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    # ===== ФИЛЬТР ПВЗ =====

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        if request.user.is_superuser:
            return qs

        if hasattr(request.user, "ownerprofile"):
            return qs.filter(point__in=request.user.ownerprofile.points.all())

        return qs.none()

    # ===== КНОПКА ОТКРЫТЬ =====

    def view_link(self, obj):
        url = reverse("admin:survey-view-clean", args=[obj.id])
        return format_html(
            '<a href="{}" class="text-blue-600 font-semibold">Открыть</a>',
            url,
        )

    view_link.short_description = "Просмотр"

    # =========================
    # DASHBOARD
    # =========================

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "rating-dashboard/",
                self.admin_site.admin_view(self.rating_dashboard_view),
                name="survey-rating-dashboard",
            ),
            path(
                "<int:survey_id>/view/",
                self.admin_site.admin_view(self.view_clean_page),
                name="survey-view-clean",
            ),
        ]
        return custom_urls + urls

    def rating_dashboard_view(self, request):

        date_from = request.GET.get("date_from")
        date_to = request.GET.get("date_to")

        surveys = Survey.objects.all()

        # 🔒 Ограничение владельца
        if not request.user.is_superuser:
            if hasattr(request.user, "ownerprofile"):
                surveys = surveys.filter(
                    point__in=request.user.ownerprofile.points.all()
                )
            else:
                surveys = surveys.none()

        # 📅 Фильтр по дате
        if date_from:
            surveys = surveys.filter(created_at__date__gte=date_from)

        if date_to:
            surveys = surveys.filter(created_at__date__lte=date_to)

        answers = Answer.objects.filter(
            survey__in=surveys,
            answer_rating__isnull=False
        )

        stats = (
            answers.values(
                "survey__point__city",
                "survey__point__name",
            )
            .annotate(
                avg_rating=Avg("answer_rating"),
                total_reviews=Count("id"),
            )
            .order_by("-avg_rating")
        )

        total_orders = surveys.count()
        total_feedback_orders = surveys.filter(completed=True).count()
        total_reviews = answers.count()

        context = dict(
            self.admin_site.each_context(request),
            stats=stats,
            total_orders=total_orders,
            total_feedback_orders=total_feedback_orders,
            total_reviews=total_reviews,
            title="Дашборд рейтингов ПВЗ",
            date_from=date_from,
            date_to=date_to,
        )

        return TemplateResponse(
            request,
            "admin/rating_dashboard.html",
            context,
        )

    # =========================
    # ЧИСТАЯ СТРАНИЦА ПРОСМОТРА
    # =========================

    def view_clean_page(self, request, survey_id):

        survey = get_object_or_404(Survey, pk=survey_id)

        # 🔒 Ограничение владельца
        if not request.user.is_superuser:
            if not hasattr(request.user, "ownerprofile"):
                return HttpResponseForbidden()

            if survey.point not in request.user.ownerprofile.points.all():
                return HttpResponseForbidden()

        answers = survey.answer_set.select_related("question").all()

        return TemplateResponse(
            request,
            "admin/survey_clean_view.html",
            {
                "survey": survey,
                "answers": answers,
            },
        )


# =========================
# USER ADMIN
# =========================

class OwnerProfileInline(admin.StackedInline):
    model = OwnerProfile
    can_delete = False
    verbose_name_plural = "Права владельца"


class CustomUserAdmin(UserAdmin):
    inlines = [OwnerProfileInline]

    # Только суперюзер видит раздел пользователей
    def has_module_permission(self, request):
        return request.user.is_superuser


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)