from unittest.mock import patch

import pytest
from django.urls import reverse

from apps.orders.models import Order
from apps.orders.services import InitiateResult

from .factories import OrderFactory

pytestmark = pytest.mark.django_db


def test_order_create_get_returns_200(client):
    response = client.get(reverse("orders:create"))
    assert response.status_code == 200


def test_order_create_prefills_package_from_querystring(client):
    response = client.get(reverse("orders:create") + "?package=starter")
    assert response.status_code == 200
    assert b'value="starter" selected' in response.content


def test_order_create_post_creates_order_and_redirects(client):
    response = client.post(
        reverse("orders:create"),
        data={
            "package": "signpost",
            "business_name": "Samwa Bakery",
            "contact_name": "Jane",
            "phone": "0776298873",
            "email": "",
            "notes": "",
        },
    )
    assert Order.objects.filter(business_name="Samwa Bakery").exists()
    order = Order.objects.get(business_name="Samwa Bakery")
    assert response.status_code == 302
    assert response.url == reverse("orders:payment_method", kwargs={"pk": order.pk})


def test_order_create_post_invalid_does_not_create_order(client):
    client.post(
        reverse("orders:create"),
        data={
            "package": "signpost",
            "business_name": "",
            "contact_name": "Jane",
            "phone": "0776298873",
            "email": "",
            "notes": "",
        },
    )
    assert not Order.objects.exists()


def test_payment_method_page_returns_200(client):
    order = OrderFactory()
    response = client.get(reverse("orders:payment_method", kwargs={"pk": order.pk}))
    assert response.status_code == 200


@patch("apps.orders.views.PaynowService")
def test_initiate_mobile_payment_redirects_to_status_on_success(mock_service_cls, client):
    mock_service_cls.return_value.initiate_mobile_payment.return_value = InitiateResult(
        success=True, poll_url="https://paynow.example/poll/1", instructions="Enter your PIN"
    )
    order = OrderFactory()

    response = client.post(
        reverse("orders:initiate_mobile", kwargs={"pk": order.pk}),
        data={"method": "ecocash", "phone": "0776298873"},
    )

    assert response.status_code == 302
    assert response.url == reverse("orders:status", kwargs={"pk": order.pk})


@patch("apps.orders.views.PaynowService")
def test_initiate_mobile_payment_redirects_back_on_failure(mock_service_cls, client):
    mock_service_cls.return_value.initiate_mobile_payment.return_value = InitiateResult(
        success=False, error="Insufficient balance"
    )
    order = OrderFactory()

    response = client.post(
        reverse("orders:initiate_mobile", kwargs={"pk": order.pk}),
        data={"method": "ecocash", "phone": "0776298873"},
    )

    assert response.status_code == 302
    assert response.url == reverse("orders:payment_method", kwargs={"pk": order.pk})


def test_initiate_mobile_payment_requires_phone(client):
    order = OrderFactory()
    response = client.post(
        reverse("orders:initiate_mobile", kwargs={"pk": order.pk}),
        data={"method": "ecocash", "phone": ""},
    )
    assert response.status_code == 302


def test_order_status_returns_200(client):
    order = OrderFactory()
    response = client.get(reverse("orders:status", kwargs={"pk": order.pk}))
    assert response.status_code == 200


def test_paynow_update_webhook_requires_post(client):
    response = client.get(reverse("orders:paynow_update"))
    assert response.status_code == 405


def test_payment_return_redirects_to_order_status_with_valid_reference(client):
    order = OrderFactory()
    response = client.get(reverse("orders:payment_return") + f"?reference=PHYB-{order.pk}")
    assert response.status_code == 302
    assert response.url == reverse("orders:status", kwargs={"pk": order.pk})


def test_payment_return_falls_back_to_home_with_no_reference(client):
    response = client.get(reverse("orders:payment_return"))
    assert response.status_code == 302
    assert response.url == reverse("core:home")


def test_payment_return_falls_back_to_home_with_unknown_order(client):
    response = client.get(reverse("orders:payment_return") + "?reference=PHYB-999999")
    assert response.status_code == 302
    assert response.url == reverse("core:home")
