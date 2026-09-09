"""Django settings for the OriginPass project."""

import os
from pathlib import Path

import dj_database_url
from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")


def require_env(name):
    value = os.getenv(name)
    if not value:
        raise ImproperlyConfigured(f"{name} is not set. Copy .env.example to .env and fill it in.")
    return value


def env_flag(name, default="False"):
    return os.getenv(name, default).strip().lower() in {"1", "true", "yes", "on"}


# Also the key every integrity signature is derived from, so rotating it
# invalidates the signature on every product, audit entry and custody record
# written before the rotation. Put the old value in SECRET_KEY_FALLBACKS when
# rotating; see audit/integrity.py.
SECRET_KEY = require_env("SECRET_KEY")
SECRET_KEY_FALLBACKS = [
    key.strip() for key in os.getenv("SECRET_KEY_FALLBACKS", "").split(",") if key.strip()
]
DEBUG = env_flag("DEBUG")
ALLOWED_HOSTS = [h.strip() for h in os.getenv("ALLOWED_HOSTS", "").split(",") if h.strip()]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "accounts",
    "companies",
    "products",
    "verification",
    "audit",
    "pages",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    # Between the session and the common middleware, which is where it can read
    # the language from the session and still act before the URL is resolved.
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# PostgreSQL only. A missing DATABASE_URL is an error rather than a silent
# fallback to another engine, so development and deployment run on the same one.
DATABASES = {"default": dj_database_url.parse(require_env("DATABASE_URL"), conn_max_age=600)}
# Fail fast when the database is not up, rather than blocking on the connect.
DATABASES["default"].setdefault("OPTIONS", {})["connect_timeout"] = 5

AUTH_USER_MODEL = "accounts.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# PBKDF2 with a per-record salt, which is what DBR11 asks for.
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.ScryptPasswordHasher",
]

LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "companies:application_detail"
LOGOUT_REDIRECT_URL = "pages:home"

# UR04 asks for the interface in Spanish; the course asks for every artefact in
# English. Both hold at once: code, comments, commit messages and documentation
# stay in English, and the interface strings are translated at render time. The
# source strings are therefore the English ones, and locale/es holds the
# translation actually served.
LANGUAGE_CODE = "es-co"
LANGUAGES = [
    ("es", "Español"),
    ("en", "English"),
]
LOCALE_PATHS = [BASE_DIR / "locale"]
TIME_ZONE = "America/Bogota"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

MESSAGE_STORAGE = "django.contrib.messages.storage.session.SessionStorage"

# Transport hardening is driven by its own variables rather than by DEBUG,
# because whether the site is served over HTTPS is a property of the
# deployment, not of whether debugging is on. A deployment behind TLS turns
# these on in its environment; see .env.example.
SECURE_SSL_REDIRECT = env_flag("SECURE_SSL_REDIRECT")
SESSION_COOKIE_SECURE = env_flag("SESSION_COOKIE_SECURE")
CSRF_COOKIE_SECURE = env_flag("CSRF_COOKIE_SECURE")
SECURE_HSTS_SECONDS = int(os.getenv("SECURE_HSTS_SECONDS", "0"))
SECURE_HSTS_INCLUDE_SUBDOMAINS = SECURE_HSTS_SECONDS > 0
SECURE_HSTS_PRELOAD = SECURE_HSTS_SECONDS > 0
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
