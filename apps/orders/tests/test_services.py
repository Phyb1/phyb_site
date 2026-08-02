"""
Tests PaynowService without ever touching the real Paynow API — the
`paynow.Paynow` client is mocked out entirely, so this suite runs offline
and never risks creating a real transaction.
"""
from unittest.mock import MagicMock, patch

import pytest

from apps.orders.models import Order, PaymentAttempt
from apps.orders.services import PaynowService

from .factories import OrderFactory

pytestmark = pytest.mark.django_db


@patch("apps.orders.services.Paynow")
def test_initiate_mobile_payment_success_updates_order(mock_paynow_cls):
    mock_client = mock_paynow_cls.return_value
    mock_client.create_payment.return_value = MagicMock()
    mock_client.send_mobile.return_value = MagicMock(
        success=True, reference="ref-123", poll_url="https://paynow.example/poll/123",
        instructions="Enter your PIN", data="{}",
    )

    order = OrderFactory()
    result = PaynowService().initiate_mobile_payment(order, "0776298873", "ecocash")

    order.refresh_from_db()
    assert result.success is True
    assert order.status == Order.Status.AWAITING_PAYMENT
    assert PaymentAttempt.objects.filter(order=order, method="ecocash").exists()


@patch("apps.orders.services.Paynow")
def test_initiate_mobile_payment_failure_leaves_order_pending(mock_paynow_cls):
    mock_client = mock_paynow_cls.return_value
    mock_client.create_payment.return_value = MagicMock()
    mock_client.send_mobile.return_value = MagicMock(
        success=False, error="Insufficient balance", reference="", poll_url="", data="{}",
    )

    order = OrderFactory()
    result = PaynowService().initiate_mobile_payment(order, "0776298873", "ecocash")

    order.refresh_from_db()
    assert result.success is False
    assert order.status == Order.Status.PENDING


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
