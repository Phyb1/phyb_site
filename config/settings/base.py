"""
Base settings shared across dev/prod. Never import environment-specific
values here directly — use decouple.config() so every setting can be
overridden by an environment variable without touching code.
"""
from pathlib import Path

from decouple import Csv, config

# Three parents up from this file: config/settings/base.py -> project root
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Falls back to an obviously-insecure key so `manage.py test`/pytest work
# out of the box with no .env file. Production MUST set a real SECRET_KEY
# via environment variable — config/settings/prod.py doesn't relax this.
SECRET_KEY = config("SECRET_KEY", default="django-insecure-dev-key-change-me")
DEBUG = config("DEBUG", default=False, cast=bool)
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="", cast=Csv())

SITE_NAME = config("SITE_NAME", default="PHYB")
SITE_DOMAIN = config("SITE_DOMAIN", default="phyb.co.zw")
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default="hello@phyb.co.zw")

# Contact details shown in nav/footer/buttons — kept out of templates so
# changing a phone number is a one-line env edit, not a template hunt.
WHATSAPP_NUMBER = config("WHATSAPP_NUMBER", default="263776298873")  # international format, no + or spaces
CONTACT_PHONE_DISPLAY = config("CONTACT_PHONE_DISPLAY", default="+263 77 629 8873")
CONTACT_EMAIL = config("CONTACT_EMAIL", default="hello@phyb.co.zw")
BUSINESS_ADDRESS = config("BUSINESS_ADDRESS", default="Mvurwi, Mashonaland Central, Zimbabwe")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
    # third party
    "django_htmx",
    "crispy_forms",
    "crispy_bootstrap5",
    # local apps
    "apps.core",
    "apps.portfolio",
    "apps.blog",
    "apps.orders",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_htmx.middleware.HtmxMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # Project-level templates dir takes priority over app templates,
        # which is what lets templates/admin/base_site.html override the
        # built-in admin templates.
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "apps.core.context_processors.site_meta",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# Default to sqlite for local dev; DATABASE_URL overrides in prod via
# config/settings/prod.py so nothing here silently talks to Postgres.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Africa/Harare"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Logging: file handler needs logs/ to exist BEFORE Passenger starts the
# app, or the whole site 500s on boot (bit us before on Shato Sports Bar).
# The logs/.gitkeep file in this repo exists for exactly this reason —
# don't delete the logs/ directory.
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{asctime} {levelname} {name} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "verbose"},
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": BASE_DIR / "logs" / "django.log",
            "maxBytes": 5 * 1024 * 1024,
            "backupCount": 3,
            "formatter": "verbose",
            "encoding":"utf-8",
        },
    },
    "root": {"handlers": ["console"], "level": "INFO"},
    "loggers": {
        "django": {"handlers": ["console", "file"], "level": "INFO", "propagate": False},
        "apps": {"handlers": ["console", "file"], "level": "INFO", "propagate": False},
    },
}

# --- Paynow (order processing / Ecocash) -----------------------------------
PAYNOW_INTEGRATION_ID = config("PAYNOW_INTEGRATION_ID", default="")
PAYNOW_INTEGRATION_KEY = config("PAYNOW_INTEGRATION_KEY", default="")
PAYNOW_RETURN_URL = config("PAYNOW_RETURN_URL", default="")
PAYNOW_RESULT_URL = config("PAYNOW_RESULT_URL", default="")
# Only needed while the Paynow integration is in test mode — see the
# comment in apps/orders/services.py::_build_payment for why. Leave unset
# in production once the integration is approved live.
PAYNOW_TEST_MODE_EMAIL = config("PAYNOW_TEST_MODE_EMAIL", default="")

LOGIN_REDIRECT_URL = "/"
