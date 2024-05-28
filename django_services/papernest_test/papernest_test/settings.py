from pathlib import Path
import environ
import os
import boto3
import json


def get_db_config(environment: str) -> dict:
    AWS_DB_ENGINE = env("AWS_DB_ENGINE")

    if environment == "PROD":
        PSS_PARAM_NAME = env("PSS_PARAM_NAME")
        ssm_client = boto3.client("ssm")
        response = ssm_client.get_parameter(
            Name=PSS_PARAM_NAME, WithDecryption=True
        )
        admin_db_password = json.loads(response["Parameter"]["Value"])[
            "admin_db_password"
        ]
    else:
        admin_db_password = env("DB_PASSWORD")

    return {
        "ENGINE": AWS_DJANGO_ENG_MAP[AWS_DB_ENGINE],
        "NAME": env("DB_NAME"),
        "USER": env("DB_USER"),
        "PASSWORD": admin_db_password,
        "HOST": env("DB_HOST"),
        "PORT": env("DB_PORT"),
    }


env = environ.Env()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = (
    "django-insecure-)yio8uz3=ozyy9a+-l_8e(b%8zi!%1m82-awvp@i_)yhx6(l_1"
)

ALLOWED_HOSTS = ["*"]


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "management.apps.ManagementConfig",
    "operators.apps.OperatorsConfig",
]

MIDDLEWARE = [
    "papernest_test.middleware.HealthCheckMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "papernest_test.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "papernest_test.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

AWS_DJANGO_ENG_MAP = {
    "aurora-postgresql": "django.contrib.gis.db.backends.postgis",
}

ENVIRONMENT = env("ENVIRONMENT")

if ENVIRONMENT == "PROD" or ENVIRONMENT == "COMPOSE":
    DATABASES = {"default": get_db_config(ENVIRONMENT)}
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.contrib.gis.db.backends.spatialite",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

DEBUG = True

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Europe/Madrid"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
