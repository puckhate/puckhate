"""Django settings for PUCKHATE!"""

import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent


def get_env_variable(name, default=None):
    # Treat an empty value the same as unset so the default applies
    value = os.environ.get(name)
    if not value:
        return default
    return value


def env_bool(name, default=False):
    # Treat an empty value the same as unset so the default applies
    value = os.environ.get(name)
    if not value:
        return default
    return value.lower() in ("1", "true", "yes", "on")


def env_list(name, default=""):
    # Treat an empty value the same as unset so the default applies
    raw = os.environ.get(name) or default
    return [item.strip() for item in raw.split(",") if item.strip()]


def env_int(name, default):
    value = os.environ.get(name, "")
    try:
        return int(value)
    except ValueError:
        return default


DEBUG = env_bool("DJANGO_DEBUG", False)
SECRET_KEY = get_env_variable("DJANGO_SECRET_KEY")
if not SECRET_KEY:
    if DEBUG:
        # Local development convenience only.
        SECRET_KEY = "dev-insecure-change-me"
    else:
        raise ImproperlyConfigured(
            "DJANGO_SECRET_KEY must be set when DEBUG is disabled."
        )

ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party
    "rest_framework",
    "corsheaders",
    "django_filters",
    # First-party
    "api",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    # Serves the SPA for unrouted GET paths. Must precede CommonMiddleware so
    # APPEND_SLASH is applied before this fallback.
    "puckhate.middleware.SPAFallbackMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "puckhate.urls"

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

WSGI_APPLICATION = "puckhate.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": get_env_variable("DB_DEFAULT_NAME", "puckhate"),
        "USER": get_env_variable("DB_DEFAULT_USER", "puckhate"),
        "PASSWORD": get_env_variable("DB_DEFAULT_PASSWORD", "puckhate"),
        "HOST": get_env_variable("DB_DEFAULT_HOST", "127.0.0.1"),
        "PORT": get_env_variable("DB_DEFAULT_PORT", "3306"),
        "CONN_MAX_AGE": env_int("CONN_MAX_AGE", 0),
        "OPTIONS": {"charset": "utf8mb4"},
    },
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": f"django.contrib.auth.password_validation.{name}"}
    for name in (
        "UserAttributeSimilarityValidator",
        "MinimumLengthValidator",
        "CommonPasswordValidator",
        "NumericPasswordValidator",
    )
]

# Logging
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {"format": "{levelname} {name}: {message}", "style": "{"},
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "simple"},
    },
    "root": {
        "handlers": ["console"],
        "level": get_env_variable("LOG_LEVEL", "INFO").upper(),
    },
    "loggers": {
        "django": {"handlers": ["console"], "level": "INFO", "propagate": False},
    },
}

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Absolute base URL used to build links in outbound admin emails
SITE_URL = get_env_variable("SITE_URL", "http://localhost:8000").rstrip("/")

# Controls the robots.txt served by puckhate.views.robots_txt
# True to allow crawlers (prod), False to disallow crawling entirely (staging)
ROBOTS_ALLOW = env_bool("ROBOTS_ALLOW", True)

# The Vite build emits the SPA (hashed assets + index.html) into this dir.
SPA_DIR = BASE_DIR / "spa"

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
# The SPA build output is collected/served as static. Only include it when
# present so `runserver` doesn't warn in dev (where Vite serves the SPA).
STATICFILES_DIRS = [SPA_DIR] if SPA_DIR.exists() else []
# Media is split into two roots by sensitivity:
# - MEDIA_* is PUBLIC (e.g. logos, images) and may be served publicly.
#   Nothing private may ever live under MEDIA_ROOT.
# - PRIVATE_MEDIA_* holds sensitive uploads (donation receipts) and is served ONLY by
#   the staff-gated `protected_media` view at /private-media/.
MEDIA_URL = "/media/"
MEDIA_ROOT = Path(get_env_variable("MEDIA_ROOT", str(BASE_DIR / "media")))
PRIVATE_MEDIA_URL = "/private-media/"
PRIVATE_MEDIA_ROOT = Path(
    get_env_variable("PRIVATE_MEDIA_ROOT", str(BASE_DIR / "private_media"))
)

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    # Receipts and any other private uploads — files land under
    # PRIVATE_MEDIA_ROOT and resolve to URLs under the gated /private/ route.
    "private": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
        "OPTIONS": {
            "location": PRIVATE_MEDIA_ROOT,
            "base_url": PRIVATE_MEDIA_URL,
        },
    },
    # Vite already content-hashes its assets, so use the non-manifest WhiteNoise storage
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}

# WhiteNoise normally detects cache-forever-able files via the manifest storage
# which we don't use, but the vite-emitted assets are content-hashed and can be
# cached forever.
WHITENOISE_IMMUTABLE_FILE_TEST = r"^/static/assets/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "PAGE_SIZE": 100,
    # Expose the browsable API only when DEBUG is enabled (local development)
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        *(["rest_framework.renderers.BrowsableAPIRenderer"] if DEBUG else []),
    ],
    # Rate limits for the unauthenticated write endpoints
    # Applied per-view via the scoped throttles in api/throttling.py
    "DEFAULT_THROTTLE_RATES": {
        "receipts": "10/min",
        "donations": "10/min",
    },
    # Number of trusted reverse proxies in front of the app
    "NUM_PROXIES": env_int("NUM_PROXIES", 1),
}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": get_env_variable("VALKEY_URL", "redis://127.0.0.1:6379/0"),
    }
}

CORS_ALLOWED_ORIGINS = env_list("CORS_ALLOWED_ORIGINS", "http://localhost:5173")
CORS_ALLOW_CREDENTIALS = True
CSRF_TRUSTED_ORIGINS = env_list("CSRF_TRUSTED_ORIGINS", "http://localhost:5173")

# HTTPS Hardening
if env_bool("SECURE_PROXY_SSL_HEADER", False):
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

SESSION_COOKIE_SECURE = env_bool("SESSION_COOKIE_SECURE", not DEBUG)
CSRF_COOKIE_SECURE = env_bool("CSRF_COOKIE_SECURE", not DEBUG)
SECURE_SSL_REDIRECT = env_bool("SECURE_SSL_REDIRECT", not DEBUG)

# HSTS. Should be enabled only in production
SECURE_HSTS_SECONDS = env_int("SECURE_HSTS_SECONDS", 0)
SECURE_HSTS_INCLUDE_SUBDOMAINS = env_bool(
    "SECURE_HSTS_INCLUDE_SUBDOMAINS", SECURE_HSTS_SECONDS > 0
)
SECURE_HSTS_PRELOAD = env_bool("SECURE_HSTS_PRELOAD", False)

# Email
# In development (DEBUG=1), mail is written to the console
EMAIL_BACKEND = get_env_variable(
    "EMAIL_BACKEND",
    "django.core.mail.backends.console.EmailBackend"
    if DEBUG
    else "django.core.mail.backends.smtp.EmailBackend",
)
EMAIL_HOST = get_env_variable("EMAIL_HOST", "localhost")
EMAIL_PORT = env_int("EMAIL_PORT", 587)
EMAIL_HOST_USER = get_env_variable("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = get_env_variable("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = env_bool("EMAIL_USE_TLS", True)
DEFAULT_FROM_EMAIL = get_env_variable(
    "DEFAULT_FROM_EMAIL", "PUCKHATE! <noreply@puckhate.com>"
)

# CurrencyLayer API
CURRENCYLAYER_API_KEY = os.environ.get("CURRENCYLAYER_API_KEY")

# HockeyTech API
HOCKEYTECH_API_KEY = get_env_variable("HOCKEYTECH_API_KEY", "")
HOCKEYTECH_PLAYER_ID = env_int("HOCKEYTECH_PLAYER_ID", 189)
HOCKEYTECH_SEASON_ID = env_int("HOCKEYTECH_SEASON_ID", 0)
# Career goals already scored before the campaign began (23 as of playoffs 2026)
HOCKEYTECH_STARTING_GOALS = env_int("HOCKEYTECH_STARTING_GOALS", 23)
