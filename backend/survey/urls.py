from django.urls import path

from .views import HealthView, PublicSurveyDetailView, PublicSurveySubmitView

urlpatterns = [
    path('public/health/', HealthView.as_view(), name='health'),
    path('public/surveys/<uuid:token>/', PublicSurveyDetailView.as_view(), name='public-survey-detail'),
    path('public/surveys/<uuid:token>/submit/', PublicSurveySubmitView.as_view(), name='public-survey-submit'),
]
