from pathlib import Path
import os

from django.urls import reverse
import dj_database_url
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'dev-secret-key')
DEBUG = True
ALLOWED_HOSTS = [h.strip() for h in os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',') if h.strip()]

INSTALLED_APPS = [
    "unfold",
    "unfold.contrib.filters",
    "unfold.contrib.forms",
    "unfold.contrib.inlines",
    "unfold.contrib.import_export",

    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "corsheaders",
    "rest_framework",
    "survey",
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'survey.middleware.BlockOwnerAdminMiddleware',
]

ROOT_URLCONF = 'survey_app.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    }
]

WSGI_APPLICATION = 'survey_app.wsgi.application'
ASGI_APPLICATION = 'survey_app.asgi.application'

DATABASES = {
    'default': dj_database_url.parse(
        os.getenv('DATABASE_URL', f'sqlite:///{BASE_DIR / "db.sqlite3"}'),
        conn_max_age=600,
    )
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = []


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CORS_ALLOWED_ORIGINS = [
    origin.strip() for origin in os.getenv('CORS_ALLOWED_ORIGINS', 'http://localhost:5173').split(',') if origin.strip()
]

REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'survey.throttling.SurveySubmitRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '1000/day',
        'survey_submit': '10/min',
    },
}

def sidebar_callback(request):

    if request.user.is_superuser:
        return {
            "navigation": [
                {
                    "title": "Администрирование",
                    "items": [
                        {
                            "title": "ПВЗ",
                            "icon": "location_on",
                            "link": "/admin/survey/point/",
                        },
                        {
                            "title": "Вопросы",
                            "icon": "help",
                            "link": "/admin/survey/question/",
                        },
                        {
                            "title": "Пользователи",
                            "icon": "group",
                            "link": "/admin/auth/user/",
                        },
                    ],
                },
                {
                    "title": "Survey",
                    "items": [
                        {
                            "title": "Опросы",
                            "icon": "description",
                            "link": "/admin/survey/survey/",
                        },
                        {
                            "title": "Рейтинги",
                            "icon": "bar_chart",
                            "link": "/admin/survey/survey/rating-dashboard/",
                        },
                    ],
                },
            ]
        }

    # 👇 Владелец ПВЗ
    return {
        "navigation": [
            {
                "title": "Опросники",
                "items": [
                    {
                        "title": "Опросы",
                        "icon": "description",
                        "link": "/admin/survey/survey/",
                    },
                    {
                        "title": "Рейтинги",
                        "icon": "bar_chart",
                        "link": "/admin/survey/survey/rating-dashboard/",
                    },
                ],
            }
        ]
    }


UNFOLD = {
    "SITE_TITLE": "Survey Admin",
    "SITE_HEADER": "Survey Platform",
    "SITE_SYMBOL": "dashboard",
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": False,
    "SIDEBAR": sidebar_callback,
}


import mimetypes
mimetypes.add_type("text/css", ".css", True)
mimetypes.add_type("application/javascript", ".js", True)