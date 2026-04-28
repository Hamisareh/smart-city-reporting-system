#notification_service/notification_service/settings.py
from pathlib import Path
from datetime import timedelta
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-fallback-key-for-dev')
DEBUG = True

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'rest_framework',
    'notification',
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
    'notification.middleware.JWTAuthMiddleware',
]

ROOT_URLCONF = 'notification_service.urls'

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
    },
]

WSGI_APPLICATION = 'notification_service.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db_notification.sqlite3',
    }
}

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Algiers'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'

# ✅ DÉSACTIVER COMPLÈTEMENT L'AUTHENTIFICATION DRF
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [],  # ← Vide
    'DEFAULT_PERMISSION_CLASSES': [],      # ← Vide
    'UNAUTHENTICATED_USER': None,          # ← Pas d'utilisateur par défaut
    'UNAUTHENTICATED_TOKEN': None,
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}

CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'