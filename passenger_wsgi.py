"""
Entry point for cPanel Passenger deployments. Passenger imports this file
directly and looks for a module-level `application` callable — it does not
run `manage.py`, so DJANGO_SETTINGS_MODULE must be set here explicitly.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.prod")

from django.core.wsgi import get_wsgi_application  # noqa: E402

application = get_wsgi_application()
