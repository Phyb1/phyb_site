"""Root-level pytest fixtures shared across all app test suites."""
import pytest
from django.contrib.auth import get_user_model


@pytest.fixture
def admin_user(db):
    User = get_user_model()
    return User.objects.create_superuser(
        username="admin", email="admin@phyb.co.zw", password="testpass123"
    )
