"""Local development settings. Run with DJANGO_SETTINGS_MODULE=config.settings.dev"""
from .base import *  # noqa: F401,F403

DEBUG = True

INSTALLED_APPS += ["debug_toolbar"]  # noqa: F405
MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")  # noqa: F405
INTERNAL_IPS = ["127.0.0.1"]

# The default INTERNAL_IPS check only shows the toolbar for requests that
# arrive from 127.0.0.1. That breaks when testing from a phone browser
# against a dev server bound to 0.0.0.0 and hit over LAN — this always
# shows the toolbar whenever DEBUG is on, which is safe since prod.py
# never imports debug_toolbar at all.
DEBUG_TOOLBAR_CONFIG = {
    "SHOW_TOOLBAR_CALLBACK": lambda request: True,
}

# Emails just print to the console locally instead of actually sending
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
