from unittest.mock import patch

import pytest
from django.contrib.admin.sites import AdminSite
from django.test import RequestFactory

from apps.orders.admin import OrderAdmin
from apps.orders.models import Order

from .factories import OrderFactory

pytestmark = pytest.mark.django_db


def _save_via_admin(order, request=None):
    admin_instance = OrderAdmin(Order, AdminSite())
    request = request or RequestFactory().post("/admin/orders/order/1/change/")
    form = type("FakeForm", (), {})()  # save_model doesn't touch form itself here
    admin_instance.save_model(request, order, form, change=True)


@patch("apps.orders.admin.send_payment_confirmed_notification")
def test_manual_paid_transition_sends_notification(mock_notify):
    """This is the whole point of the hook: direct EcoCash transfers have
    no webhook, so marking PAID by hand in /admin/ must trigger the same
    email the Paynow webhook path sends."""
    order = OrderFactory(status=Order.Status.AWAITING_PAYMENT)
    order.status = Order.Status.PAID

    _save_via_admin(order)

    mock_notify.assert_called_once_with(order)


@patch("apps.orders.admin.send_payment_confirmed_notification")
def test_resaving_already_paid_order_does_not_resend(mock_notify):
    order = OrderFactory(status=Order.Status.PAID)
    order.business_name = "Updated Name"  # any unrelated re-save

    _save_via_admin(order)

    mock_notify.assert_not_called()


@patch("apps.orders.admin.send_payment_confirmed_notification")
def test_non_paid_transition_does_not_send(mock_notify):
    order = OrderFactory(status=Order.Status.PENDING)
    order.status = Order.Status.CANCELLED

    _save_via_admin(order)

    mock_notify.assert_not_called()
