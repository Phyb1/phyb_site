"""
Tests PaynowService without ever touching the real Paynow API.

Transaction initiation is mocked at the `_post_and_parse` level (our own
function) rather than mocking `paynow.Paynow.send`/`send_mobile` — those
methods aren't called anymore; see the module docstring in services.py for
why. Status polling still goes through the SDK's `Paynow` class, which is
mocked the old way since that part of the SDK is still used as-is.
"""
from unittest.mock import MagicMock, patch

import pytest

from apps.orders.models import Order, PaymentAttempt
from apps.orders.services import PaynowService, _paynow_hash

from .factories import OrderFactory

pytestmark = pytest.mark.django_db


# --- _paynow_hash -----------------------------------------------------------

def test_paynow_hash_excludes_existing_hash_key():
    fields_without = {"a": "1", "b": "2"}
    fields_with = {"a": "1", "b": "2", "hash": "shouldbeignored"}
    assert _paynow_hash(fields_without, "key123") == _paynow_hash(fields_with, "key123")


def test_paynow_hash_is_order_sensitive():
    forward = _paynow_hash({"a": "1", "b": "2"}, "key123")
    backward = _paynow_hash({"b": "2", "a": "1"}, "key123")
    assert forward != backward


def test_paynow_hash_is_deterministic():
    fields = {"a": "1", "b": "2"}
    assert _paynow_hash(fields, "key123") == _paynow_hash(fields, "key123")


# --- authemail resolution ----------------------------------------------------

@patch("apps.orders.services.Paynow")
def test_resolve_authemail_uses_order_email_by_default(mock_paynow_cls):
    order = OrderFactory(email="customer@example.com")
    assert PaynowService()._resolve_authemail(order) == "customer@example.com"


@patch("apps.orders.services.Paynow")
def test_resolve_authemail_falls_back_to_contact_email_when_order_email_blank(mock_paynow_cls, settings):
    settings.CONTACT_EMAIL = "hello@phyb.co.zw"
    order = OrderFactory(email="")
    assert PaynowService()._resolve_authemail(order) == "hello@phyb.co.zw"


@patch("apps.orders.services.Paynow")
def test_resolve_authemail_test_mode_overrides_order_email(mock_paynow_cls, settings):
    """PAYNOW_TEST_MODE_EMAIL must win even when the order has its own
    email — this is the whole point of the override, since Paynow's test
    mode rejects any authemail that isn't the merchant's registered one."""
    settings.PAYNOW_TEST_MODE_EMAIL = "merchant@phyb.co.zw"
    order = OrderFactory(email="customer@example.com")
    assert PaynowService()._resolve_authemail(order) == "merchant@phyb.co.zw"


# --- initiate_mobile_payment / initiate_web_checkout -------------------------

@patch("apps.orders.services._post_and_parse")
@patch("apps.orders.services.Paynow")
def test_initiate_mobile_payment_success_updates_order(mock_paynow_cls, mock_post_and_parse):
    mock_post_and_parse.return_value = {
        "status": "Ok",
        "pollurl": "https://paynow.example/poll/123",
        "instructions": "Enter your PIN",
    }

    order = OrderFactory()
    result = PaynowService().initiate_mobile_payment(order, "0776298873", "ecocash")

    order.refresh_from_db()
    assert result.success is True
    assert result.poll_url == "https://paynow.example/poll/123"
    assert order.status == Order.Status.AWAITING_PAYMENT
    assert PaymentAttempt.objects.filter(order=order, method="ecocash").exists()


@patch("apps.orders.services._post_and_parse")
@patch("apps.orders.services.Paynow")
def test_initiate_mobile_payment_failure_leaves_order_pending_and_surfaces_real_error(
    mock_paynow_cls, mock_post_and_parse
):
    """This is the exact bug that broke production: Paynow's real error
    message must reach the user, not get swallowed."""
    mock_post_and_parse.return_value = {
        "status": "Error",
        "error": "The ResultUrl must start with http:// or https://",
    }

    order = OrderFactory()
    result = PaynowService().initiate_mobile_payment(order, "0776298873", "ecocash")

    order.refresh_from_db()
    assert result.success is False
    assert result.error == "The ResultUrl must start with http:// or https://"
    assert order.status == Order.Status.PENDING


@patch("apps.orders.services._post_and_parse")
@patch("apps.orders.services.Paynow")
def test_initiate_mobile_payment_failure_without_error_field_falls_back_to_status(
    mock_paynow_cls, mock_post_and_parse
):
    mock_post_and_parse.return_value = {"status": "Error"}

    order = OrderFactory()
    result = PaynowService().initiate_mobile_payment(order, "0776298873", "ecocash")

    assert result.success is False
    assert result.error  # falls back to status/generic message, never blank


@patch("apps.orders.services._post_and_parse")
@patch("apps.orders.services.Paynow")
def test_initiate_web_checkout_success_returns_redirect_url(mock_paynow_cls, mock_post_and_parse):
    mock_post_and_parse.return_value = {
        "status": "Ok",
        "pollurl": "https://paynow.example/poll/456",
        "browserurl": "https://paynow.example/pay/456",
    }

    order = OrderFactory()
    result = PaynowService().initiate_web_checkout(order)

    assert result.success is True
    assert result.redirect_url == "https://paynow.example/pay/456"


@patch("apps.orders.services._post_and_parse")
@patch("apps.orders.services.Paynow")
def test_initiate_sends_raw_unencoded_values_not_pre_encoded(mock_paynow_cls, mock_post_and_parse):
    """Regression test for the double-encoding bug: fields passed to
    _post_and_parse must be raw values, since _post_and_parse (via
    requests) does the URL-encoding itself. If something upstream started
    pre-encoding again, this would catch it."""
    mock_post_and_parse.return_value = {"status": "Ok", "pollurl": "https://paynow.example/poll/1"}

    order = OrderFactory()
    PaynowService().initiate_web_checkout(order)

    _, sent_fields = mock_post_and_parse.call_args[0]
    assert sent_fields["resulturl"].startswith("https://")  # not "https%3A%2F%2F..."
    assert "%" not in sent_fields["resulturl"]


# --- check_status / sync_attempt_status (still uses the SDK directly) -------

@patch("apps.orders.services.Paynow")
def test_sync_attempt_status_marks_order_paid(mock_paynow_cls):
    mock_client = mock_paynow_cls.return_value
    mock_client.check_transaction_status.return_value = MagicMock(status="Paid")

    order = OrderFactory(status=Order.Status.AWAITING_PAYMENT)
    attempt = PaymentAttempt.objects.create(
        order=order, method="ecocash", poll_url="https://paynow.example/poll/123"
    )

    PaynowService().sync_attempt_status(attempt)

    order.refresh_from_db()
    attempt.refresh_from_db()
    assert order.status == Order.Status.PAID
    assert attempt.paynow_status == "paid"


@patch("apps.orders.services.Paynow")
def test_sync_attempt_status_marks_order_cancelled(mock_paynow_cls):
    mock_client = mock_paynow_cls.return_value
    mock_client.check_transaction_status.return_value = MagicMock(status="Cancelled")

    order = OrderFactory(status=Order.Status.AWAITING_PAYMENT)
    attempt = PaymentAttempt.objects.create(
        order=order, method="ecocash", poll_url="https://paynow.example/poll/123"
    )

    PaynowService().sync_attempt_status(attempt)

    order.refresh_from_db()
    assert order.status == Order.Status.CANCELLED
