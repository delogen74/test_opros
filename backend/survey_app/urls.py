from django.contrib import admin
from django.urls import path, include
from survey.views import custom_login_view, custom_logout_view, owner_dashboard_view, owner_survey_detail

urlpatterns = [
    # 🔐 Авторизация
    path("", custom_login_view, name="login"),
    path("logout/", custom_logout_view, name="logout"),

    # 👤 Дашборд владельца (НЕ внутри api!)
    path("dashboard/", owner_dashboard_view, name="owner-dashboard"),
    path("dashboard/survey/<int:pk>/", owner_survey_detail, name="owner-survey-detail"),

    # ⚙ Админка
    path("admin/", admin.site.urls),

    # 🌍 API
    path("api/v1/", include("survey.urls")),
]
