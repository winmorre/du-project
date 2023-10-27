"""
Django settings for account_serv project.

Generated by 'django-admin startproject' using Django 4.2.6.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""
import os
from pathlib import Path
from datetime import timedelta
from collections import namedtuple

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("SECRET_KEY", 'django-insecure-6-shd8d41=w$4@mil(1u_l!_c4t9+8ko!kk9kjk^w2^qu$dkk5')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    "*"
]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # third party aps
    "corsheaders",

    # local apps
    "account.apps.AccountConfig",
    "team.apps.TeamConfig",
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    "corsheaders.middleware.CorsMiddleware",
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'account_serv.urls'

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
            ],
        },
    },
]

WSGI_APPLICATION = 'account_serv.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get("POSTGRES_DB", 'pipa'),
        'USER': os.environ.get("POSTGRES_USER", 'pipa'),
        'PASSWORD': os.environ.get("POSTGRES_PASSWORD", 'pipa-secret@'),
        'PORT': int(os.environ.get("POSTGRES_PORT", '5432')),
        'HOST': os.environ.get("POSTGRES_HOST", 'localhost'),
        'TEST': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
}

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# App config values
ACCOUNT_SERVICE_LOG_PATH = ""
ACCOUNT_SERVICE_TRACE_PATH = ""
JAEGER_PARAMS = {
    "service": "",
}

RedisConfig = namedtuple("RedisConfig", "url,password,db,hash,host,port,ttl")

REDIS_TTL = 60 * 20
REDIS_PREFIX = "REDIS_"
REDIS_CONFIG = RedisConfig(
    url=os.getenv(f"{REDIS_PREFIX}URL", ""),
    db=os.getenv(f"{REDIS_PREFIX}DB", ""),
    password=os.getenv(f"{REDIS_PREFIX}PASSWORD", ""),
    hash=os.getenv(f"{REDIS_PREFIX}HASH_KEY", "redis-hash"),
    host=os.getenv(f"{REDIS_PREFIX}HOST", "localhost"),
    port=os.getenv(f"{REDIS_PREFIX}PORT", 3456),
    ttl=os.getenv(f"{REDIS_PREFIX}TTL", REDIS_TTL)
)

CREATE_SESSION_ON_LOGIN = True

VERIFYING_KEY = os.environ.get("VERIFYING_KEY")
SIGNING_KEY = os.environ.get("SIGNING_KEY")

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=5),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": False,
    "UPDATE_LAST_LOGIN": False,
    "ALGORITHM": "RS256",
    "SIGNING_KEY": SIGNING_KEY or SECRET_KEY,
    "VERIFYING_KEY": VERIFYING_KEY,
    "AUDIENCE": None,
    "ISSUER": None,
    "JSON_ENCODER": None,
    "JWK_URL": None,
    "LEEWAY": 0,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "account_id",
}
