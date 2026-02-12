from django.urls import path
from . import views

urlpatterns = [
    path("dashboard/", views.owner_dashboard_view, name="owner-dashboard"),
    path("dashboard/survey/<int:pk>/", views.owner_survey_detail, name="owner-survey-detail"),

    # API оставляем отдельно
    path('public/health/', views.HealthView.as_view(), name='health'),
    path('public/surveys/<uuid:token>/', views.PublicSurveyDetailView.as_view(), name='public-survey-detail'),
    path('public/surveys/<uuid:token>/submit/', views.PublicSurveySubmitView.as_view(), name='public-survey-submit'),
]
