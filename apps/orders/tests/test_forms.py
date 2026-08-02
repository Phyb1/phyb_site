import pytest

from apps.orders.forms import OrderForm
from apps.orders.models import Package


@pytest.mark.django_db
def test_valid_form():
    form = OrderForm(
        data={
            "package": Package.SIGNPOST,
            "business_name": "Samwa Bakery",
            "contact_name": "Jane",
            "phone": "0776298873",
            "email": "jane@example.com",
            "notes": "",
        }
    )
    assert form.is_valid()


@pytest.mark.django_db
def test_invalid_phone_rejected():
    form = OrderForm(
        data={
            "package": Package.SIGNPOST,
            "business_name": "Samwa Bakery",
            "contact_name": "Jane",
            "phone": "abc",
            "email": "",
            "notes": "",
        }
    )
    assert not form.is_valid()
    assert "phone" in form.errors


@pytest.mark.django_db
def test_missing_business_name_rejected():
    form = OrderForm(
        data={
            "package": Package.SIGNPOST,
            "business_name": "",
            "contact_name": "Jane",
            "phone": "0776298873",
            "email": "",
            "notes": "",
        }
    )
    assert not form.is_valid()
    assert "business_name" in form.errors
