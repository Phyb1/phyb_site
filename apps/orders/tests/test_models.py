from decimal import Decimal

import pytest

from apps.orders.models import Order, Package, PACKAGE_PRICES

from .factories import OrderFactory

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    "package", [Package.SIGNPOST, Package.BASIC, Package.STANDARD, Package.PREMIUM]
)
def test_amount_auto_set_from_package(package):
    order = OrderFactory(package=package)
    assert order.amount == PACKAGE_PRICES[package]


def test_signpost_amount_is_25():
    order = OrderFactory(package=Package.SIGNPOST)
    assert order.amount == Decimal("25.00")


def test_basic_amount_is_120():
    order = OrderFactory(package=Package.BASIC)
    assert order.amount == Decimal("120.00")


def test_standard_amount_is_250():
    order = OrderFactory(package=Package.STANDARD)
    assert order.amount == Decimal("250.00")


def test_premium_amount_is_370():
    order = OrderFactory(package=Package.PREMIUM)
    assert order.amount == Decimal("370.00")


def test_default_status_is_pending():
    order = OrderFactory()
    assert order.status == Order.Status.PENDING


def test_is_paid_property():
    order = OrderFactory(status=Order.Status.PAID)
    assert order.is_paid is True

    order.status = Order.Status.PENDING
    assert order.is_paid is False
