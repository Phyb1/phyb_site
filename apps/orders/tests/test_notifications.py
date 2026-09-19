from unittest.mock import patch

import pytest
from django.core import mail
from django.test import RequestFactory
from django.urls import reverse

from apps.orders.models import Package
from apps.orders.notifications import send_new_order_notification, send_payment_confirmed_notification

from .factories import OrderFactory

pytestmark = pytest.mark.django_db


def test_sends_one_email():
    order = OrderFactory(business_name="Samwa Bakery")
    send_new_order_notification(order)
    assert len(mail.outbox) == 1


def test_email_recipient_is_contact_email(settings):
    settings.CONTACT_EMAIL = "owner@phyb.co.zw"
    order = OrderFactory()
    send_new_order_notification(order)
    assert mail.outbox[0].to == ["owner@phyb.co.zw"]


def test_email_subject_includes_business_name_and_package():
    order = OrderFactory(business_name="Samwa Bakery")
    send_new_order_notification(order)
    subject = mail.outbox[0].subject
    assert "Samwa Bakery" in subject
    assert order.get_package_display() in subject


def test_email_body_includes_order_details():
    order = OrderFactory(business_name="Samwa Bakery", phone="0776298873", notes="Needs a delivery menu")
    send_new_order_notification(order)
    body = mail.outbox[0].body
    assert "Samwa Bakery" in body
    assert "0776298873" in body
    assert "Needs a delivery menu" in body
    assert str(order.amount) in body


def test_email_body_uses_absolute_admin_url_when_request_given():
    order = OrderFactory()
    request = RequestFactory().get("/")
    send_new_order_notification(order, request=request)
    body = mail.outbox[0].body
    assert body.count("http://testserver") == 1


def test_email_body_uses_relative_admin_url_without_request():
    order = OrderFactory()
    send_new_order_notification(order)
    body = mail.outbox[0].body
    assert "/admin/" in body


@patch("apps.orders.notifications.send_mail")
def test_returns_false_and_does_not_raise_on_smtp_failure(mock_send_mail):
    mock_send_mail.side_effect = ConnectionError("SMTP connection refused")
    order = OrderFactory()

    result = send_new_order_notification(order)  # must not raise

    assert result is False


@patch("apps.orders.views.send_new_order_notification")
def test_order_create_view_calls_notification_and_still_redirects_on_email_failure(
    mock_notify, client
):
    """The core guarantee: a customer's order must succeed even if the
    notification email fails outright."""
    mock_notify.return_value = False

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

    assert response.status_code == 302
    mock_notify.assert_called_once()


# --- send_payment_confirmed_notification -------------------------------------

def test_payment_confirmed_sends_one_email():
    order = OrderFactory(business_name="Samwa Bakery")
    send_payment_confirmed_notification(order)
    assert len(mail.outbox) == 1


def test_payment_confirmed_subject_says_payment_received():
    order = OrderFactory(business_name="Samwa Bakery")
    send_payment_confirmed_notification(order)
    subject = mail.outbox[0].subject
    assert "Payment received" in subject
    assert "Samwa Bakery" in subject


def test_payment_confirmed_body_includes_order_details():
    order = OrderFactory(business_name="Samwa Bakery")
    send_payment_confirmed_notification(order)
    body = mail.outbox[0].body
    assert "Samwa Bakery" in body
    assert str(order.amount) in body


@patch("apps.orders.notifications.send_mail")
def test_payment_confirmed_returns_false_and_does_not_raise_on_smtp_failure(mock_send_mail):
    mock_send_mail.side_effect = ConnectionError("SMTP connection refused")
    order = OrderFactory()

    result = send_payment_confirmed_notification(order)  # must not raise

    assert result is False


def test_payment_confirmed_includes_generator_hint_for_signpost():
    order = OrderFactory(package=Package.SIGNPOST)
    send_payment_confirmed_notification(order)
    body = mail.outbox[0].body
    assert "export_signpost_config" in body
    assert f"export_signpost_config {order.pk}" in body


def test_payment_confirmed_omits_generator_hint_for_other_packages():
    order = OrderFactory(package=Package.BASIC)
    send_payment_confirmed_notification(order)
    body = mail.outbox[0].body
    assert "export_signpost_config" not in body
