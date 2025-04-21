import os 
from pathlib import Path

from django.utils.translation import gettext_lazy as _

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
LOGIN_URL = 'login'

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-hdmj$(=rq)njm&1*xrby8i%*i+avy3c38+7^0*89rdarp_ag!k'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

AUTH_USER_MODEL = 'base.User'


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'base',
    'incident',
    'planaction',
    'faq',
    'reward',
    'dashboard',
    'crispy_forms',
    'dal',
    'dal_select2',
    'django_json_widget',
    'django_fsm',
    'celery',
    'django_filters',
    'rest_framework',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'worksafety2.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'worksafety2.context_processors.language_code', 
            ],
        },
    },
]

WSGI_APPLICATION = 'worksafety2.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'worksafety_db',
        'USER': 'postgres',
        'PASSWORD': 'postgresql',
        'HOST': '127.0.0.1',
        'PORT': '5433',
    }
}



# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'fr'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

LANGUAGES = [
    ("fr", _("French")),
    ("en", _("English")),
    ("ar", _("Arabic")),
]
LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale'),
]

LANGUAGE_BIDI = True  # Activer la prise en charge RTL
LANGUAGE_BIDI = ['ar']

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'  # URL prefix for static files

# Define the base URL for serving media files
MEDIA_URL = '/media/'  # URL prefix for media files
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')  # Directory for user-uploaded files

# Directories where Django will look for static files during development
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'base', 'static'),  # Root static directory
]


# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LONGITUDE_MIN_MAX = (-180, 180)
LATITUDE_MIN_MAX = (-90, 90)


CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_TIMEZONE = 'America/New_York'

# settings.py
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    # Bonus hebdomadaire (tous les lundis à minuit)
    'calculate-weekly-bonus': {
        'task': 'reward.tasks.calculate_weekly_bonus',
        'schedule': crontab(day_of_week='mon', hour=0, minute=0),
    },
    # Bonus mensuel (le premier jour du mois à minuit)
    'calculate-monthly-bonus': {
        'task': 'reward.tasks.calculate_monthly_bonus',
        'schedule': crontab(day_of_month=1, hour=0, minute=0),
    },
    # Bonus trimestriel (le premier jour du trimestre à minuit)
    'calculate-quarterly-bonus': {
        'task': 'reward.tasks.calculate_quarterly_bonus',
        'schedule': crontab(month_of_year='*/3', day_of_month=1, hour=0, minute=0),
    },
}