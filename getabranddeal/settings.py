"""
Django settings for getabranddeal project.

Generated by 'django-admin startproject' using Django 4.1.3.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""

import os
from pathlib import Path

if os.getenv("CI_CD_STAGE", None) is None:
    print("LOADING ENV")
    # Only loads in dev environment
    from dotenv import load_dotenv

    load_dotenv(dotenv_path=".env")

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ["SECRET_KEY"]

DEV_STAGE = "development"
TEST_STAGE = "testing"
PROD_STAGE = "production"

# SECURITY WARNING: don't run with debug turned on in production!
CI_CD_STAGE = os.environ["CI_CD_STAGE"]

if CI_CD_STAGE == PROD_STAGE:
    DEBUG = False
elif CI_CD_STAGE == TEST_STAGE or CI_CD_STAGE == DEV_STAGE:
    DEBUG = True

ALLOWED_HOSTS = ["*"]


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework.authtoken",
    "corsheaders",
    "knox",
    "authentication",
    "yt",
    "emails",
    "payments",
    "health",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "getabranddeal.urls"

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

WSGI_APPLICATION = "getabranddeal.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ["RDS_DB_NAME"],
        "USER": os.environ["RDS_USERNAME"],
        "PASSWORD": os.environ["RDS_PASSWORD"],
        "HOST": os.environ["RDS_HOSTNAME"],
        "PORT": os.environ["RDS_PORT"],
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/


AWS_S3_ACCESS_KEY_ID = os.environ["AWS_S3_ACCESS_KEY_ID"]
AWS_S3_SECRET_ACCESS_KEY = os.environ["AWS_S3_SECRET_ACCESS_KEY"]
AWS_STORAGE_BUCKET_NAME = os.environ["AWS_STORAGE_BUCKET_NAME"]
AWS_S3_REGION_NAME = os.environ["AWS_S3_REGION_NAME"]
AWS_S3_CUSTOM_DOMAIN = os.environ["AWS_S3_CUSTOM_DOMAIN"]
AWS_QUERYSTRING_AUTH = False

MEDIA_URL = "https://{}/media/".format(AWS_S3_CUSTOM_DOMAIN)
DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"


if CI_CD_STAGE == DEV_STAGE:
    STATIC_URL = "/static/"
    STATIC_ROOT = os.path.join(BASE_DIR, "static")

elif CI_CD_STAGE == TEST_STAGE or CI_CD_STAGE == PROD_STAGE:
    STATIC_URL = "https://{}/static/".format(AWS_S3_CUSTOM_DOMAIN)
    STATICFILES_STORAGE = "storages.backends.s3boto3.S3StaticStorage"

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

################################################################################
AUTH_USER_MODEL = "authentication.User"

################################################################################
# Google OAuth
GOOGLE_CLIENT_ID = os.environ["GOOGLE_CLIENT_ID"]
GOOGLE_CLIENT_SECRET = os.environ["GOOGLE_CLIENT_SECRET"]

################################################################################
# Google API
GOOGLE_API_KEY = os.environ["GOOGLE_API_KEY"]

################################################################################
# Email
CREATOR_MAIL_DOMAIN = os.environ["CREATOR_MAIL_DOMAIN"]


################################################################################
# Resend
RESEND_API_KEY = os.environ["RESEND_API_KEY"]
RESEND_WEBHOOK_SIGNING_KEY = os.environ["RESEND_WEBHOOK_SIGNING_KEY"]

################################################################################
# Celery
REDIS_URL = os.environ["REDIS_URL"]

CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"

################################################################################
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:3000",
    "https://*.getabranddeal.com",
]

if CI_CD_STAGE == DEV_STAGE:
    CSRF_TRUSTED_ORIGINS.append(
        "https://*.ngrok-free.app",
    )

################################################################################
# CORS
CORS_ALLOWED_ORIGINS = ["http://localhost:3000"]
CORS_ALLOWED_ORIGIN_REGEXES = [r"^https://\w+\.getabranddeal\.com$"]

if CI_CD_STAGE == DEV_STAGE:
    CORS_ALLOWED_ORIGIN_REGEXES.append(
        r"^https://\w+\.ngrok-free\.app$",
    )

CORS_ALLOW_METHODS = ["GET", "POST"]

################################################################################
# Stripe
STRIPE_API_KEY = os.environ["STRIPE_API_KEY"]
STRIPE_WEBHOOK_SECRET = os.environ["STRIPE_WEBHOOK_SECRET"]
