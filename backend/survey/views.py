from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Question, Survey
from .serializers import SubmitSurveySerializer, SurveyPublicSerializer
from .throttling import SurveySubmitRateThrottle


class HealthView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        return Response({'status': 'ok'})


def get_survey_questions(survey: Survey):
    categories = [Question.Category.COMMON]
    if survey.service_type in [Survey.ServiceType.PICKUP, Survey.ServiceType.BOTH]:
        categories.append(Question.Category.PICKUP)
    if survey.service_type in [Survey.ServiceType.TIRE_SERVICE, Survey.ServiceType.BOTH]:
        categories.append(Question.Category.TIRE_SERVICE)

    return Question.objects.filter(is_active=True, category__in=categories).order_by('order', 'id')


class PublicSurveyDetailView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, token):
        survey = get_object_or_404(Survey.objects.select_related('point'), token=token)
        questions = get_survey_questions(survey)
        serializer = SurveyPublicSerializer(survey, context={'questions': questions})
        return Response(serializer.data)


class PublicSurveySubmitView(APIView):
    authentication_classes = []
    permission_classes = []
    throttle_classes = [SurveySubmitRateThrottle]

    @transaction.atomic
    def post(self, request, token):
        survey = get_object_or_404(Survey.objects.select_related('point'), token=token)
        if survey.completed:
            return Response({'detail': 'Survey already completed.'}, status=status.HTTP_409_CONFLICT)

        questions = get_survey_questions(survey)
        serializer = SubmitSurveySerializer(
            data=request.data,
            context={'survey': survey, 'questions': questions},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        survey.completed = True
        survey.completed_at = timezone.now()
        survey.save(update_fields=['completed', 'completed_at'])

        rating_answers = survey.answers.exclude(answer_rating__isnull=True).values_list('answer_rating', flat=True)
        all_ratings_good = bool(rating_answers) and all(r >= 4 for r in rating_answers)

        response_data = {'show_review_page': all_ratings_good, 'review_links': None}
        if all_ratings_good:
            response_data['review_links'] = {
                '2gis': survey.point.review_link_2gis,
                'yandex': survey.point.review_link_yandex,
            }

        return Response(response_data, status=status.HTTP_200_OK)
