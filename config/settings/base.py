import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent

load_dotenv(BASE_DIR / ".env")

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv("DEBUG", "False") == "True"



# config/settings/development.py

ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    ".ngrok-free.dev",  # Wildcard allowing all *.ngrok-free.dev domains
    ".ngrok-free.app",  # Wildcard allowing all *.ngrok-free.app domains
    ".ngrok.io",        # Standard ngrok domain wildcard
]

# Required for POST requests / forms / logins to work over ngrok HTTPS
CSRF_TRUSTED_ORIGINS = [
    "https://*.ngrok-free.dev",
    "https://*.ngrok-free.app",
    "https://*.ngrok.io",
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'apps.accounts',
    'apps.restaurant',
    'apps.dashboard',
    'apps.tables',
    'apps.orders',
    'apps.menu',
    'apps.billing',
    'apps.reports',
    'apps.inventory',
    'apps.settings',
    'apps.api',
    "widget_tweaks",
    'apps.core',
    'apps.backup',
    'apps.purchase',
    'apps.stock',
    'apps.recipes',
    "pwa",
    "corsheaders",
]

# config/settings/development.py

# Direct Django to trust the domain passed in X-Forwarded-Host header from ngrok/proxy
USE_X_FORWARDED_HOST = True
USE_X_FORWARDED_PORT = True

# Trust HTTPS proxy headers sent by ngrok
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# config/settings/development.py

# ----------------------------------------------------------
# SESSION & COOKIE ISOLATION
# ----------------------------------------------------------
SESSION_COOKIE_NAME = "rms_sessionid"
CSRF_COOKIE_NAME = "rms_csrftoken"

# Ensure every device gets its own independent session
SESSION_ENGINE = "django.contrib.sessions.backends.db"
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# Cookie security for ngrok HTTPS
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = False

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    
    "django.middleware.security.SecurityMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",

    "django.middleware.common.CommonMiddleware",

    "django.middleware.csrf.CsrfViewMiddleware",

    "django.contrib.auth.middleware.AuthenticationMiddleware",

    "config.middleware.NoCacheAuthenticatedMiddleware",

    "django.contrib.messages.middleware.MessageMiddleware",

    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.restaurant.context_processors.currency_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# Supports both SQLite and PostgreSQL

DB_ENGINE = os.getenv("DB_ENGINE", "sqlite")

if DB_ENGINE == "postgres":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv("DB_NAME"),
            "USER": os.getenv("DB_USER"),
            "PASSWORD": os.getenv("DB_PASSWORD"),
            "HOST": os.getenv("DB_HOST"),
            "PORT": os.getenv("DB_PORT"),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / os.getenv("DB_NAME", "db.sqlite3"),
        }
    }
AUTH_USER_MODEL = "accounts.User"

# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
]


# Internationalization
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = "Asia/Kolkata"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/

STATIC_URL = "static/"

STATICFILES_DIRS = [
    BASE_DIR / "static",
]

MEDIA_URL = "/media/"

MEDIA_ROOT = BASE_DIR / "media"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/accounts/login/"
LOGIN_URL = "/accounts/login/"

PWA_APP_NAME = "Restaurant RMS"

PWA_APP_DESCRIPTION = "Restaurant Management System"

PWA_APP_THEME_COLOR = "#2563eb"

PWA_APP_BACKGROUND_COLOR = "#ffffff"

PWA_APP_DISPLAY = "standalone"

PWA_APP_SCOPE = "/"

PWA_APP_ORIENTATION = "any"

PWA_APP_START_URL = "/orders/floor/"

PWA_APP_STATUS_BAR_COLOR = "default"

PWA_APP_ICONS = [
    {
        "src": "/static/icons/icon-192.png",
        "sizes": "192x192",
        "type": "image/png",
    },
    {
        "src": "/static/icons/icon-512.png",
        "sizes": "512x512",
        "type": "image/png",
    },
]

PWA_APP_SPLASH_SCREEN = [
    {
        "src": "/static/icons/icon-512.png",
        "media": "(device-width: 320px)",
    }
]

PWA_APP_DIR = "ltr"

PWA_APP_LANG = "en-US"

PWA_APP_SHORTCUTS = []

PWA_APP_SCREENSHOTS = []

PWA_SERVICE_WORKER_PATH = BASE_DIR / "static" / "sw.js"

# ==========================================================
# CORS CONFIGURATION
# ==========================================================

CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
    "ngrok-skip-browser-warning",
]

CSRF_TRUSTED_ORIGINS = [
    "http://127.0.0.1:8000",
    "http://localhost:8000",
    "https://*.ngrok-free.app",
    "https://*.ngrok.io",
]