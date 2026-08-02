"""
Production settings for cPanel/Passenger deployment.
Run with DJANGO_SETTINGS_MODULE=config.settings.prod
"""
from decouple import config

from .base import *  # noqa: F401,F403

DEBUG = False

if SECRET_KEY == "django-insecure-dev-key-change-me":  # noqa: F405
    raise RuntimeError(
        "SECRET_KEY is not set. Set a real SECRET_KEY environment variable "
        "before running in production."
    )

SECURE_SSL_REDIRECT = config("SECURE_SSL_REDIRECT", default=True, cast=bool)
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 60 * 60 * 24 * 7
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Postgres if DATABASE_URL is set (typical for a real host); otherwise the
# sqlite default from base.py stays in effect, which is fine for a small
# single-tenant cPanel deployment.
_database_url = config("DATABASE_URL", default="")
if _database_url:
    import dj_database_url

    DATABASES["default"] = dj_database_url.parse(_database_url, conn_max_age=600)

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = config("EMAIL_HOST", default="")
EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=True, cast=bool)
