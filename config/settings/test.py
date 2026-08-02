"""Settings used when running the test suite (pytest-django reads this via
pytest.ini's DJANGO_SETTINGS_MODULE). Kept separate from dev.py so tests
never depend on debug_toolbar or other dev-only conveniences."""
from .base import *  # noqa: F401,F403

DEBUG = False
ALLOWED_HOSTS = ["testserver", "127.0.0.1", "localhost"]

# Fast, insecure hasher — this is only ever used for throwaway test users.
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# Skip whitenoise's manifest lookup in tests since collectstatic isn't run.
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

# Never actually hit Paynow in tests.
PAYNOW_INTEGRATION_ID = "test-id"
PAYNOW_INTEGRATION_KEY = "test-key"
PAYNOW_RETURN_URL = "http://testserver/orders/payment/return/"
PAYNOW_RESULT_URL = "http://testserver/orders/payment/update/"
