"""
Email notifications for the orders app.

Kept in a separate module (rather than inline in views.py/services.py) so
it's easy to test in isolation and easy to reason about: sending either of
these emails must never be able to break the customer-facing flow, even if
SMTP is misconfigured or the mail server is down. Both public functions
share that guarantee via the same _send() helper below.
"""
import logging

from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse

from .models import Order, Package

logger = logging.getLogger("apps.orders")


def _order_details(order: Order) -> str:
    return (
        f"Business: {order.business_name}\n"
        f"Contact: {order.contact_name}\n"
        f"Phone: {order.phone}\n"
        f"Email: {order.email or '(not provided)'}\n"
        f"Package: {order.get_package_display()}\n"
        f"Amount: ${order.amount}\n"
        f"Notes: {order.notes or '(none)'}\n"
    )


def _send(subject: str, body: str, order_pk: int) -> bool:
    """Shared send + failure handling. Returns True/False for whether it
    actually sent rather than raising, so a broken SMTP config can never
    propagate into whatever request triggered the notification."""
    try:
        send_mail(
            subject=subject,
            message=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.CONTACT_EMAIL],
            fail_silently=False,
        )
    except Exception:
        # Broad except is deliberate: SMTP failures show up as many
        # different exception types (auth, connection, timeout, DNS) and
        # none of them should ever propagate into the calling request.
        logger.exception("Failed to send notification email for order id=%s", order_pk)
        return False
    return True


def send_new_order_notification(order: Order, request=None) -> bool:
    """Sent as soon as a lead submits the order form, before any payment —
    a heads-up that someone's in the funnel, not a payment confirmation."""
    admin_path = reverse("admin:orders_order_change", args=[order.pk])
    admin_url = request.build_absolute_uri(admin_path) if request else admin_path

    subject = f"New order: {order.business_name} \u2014 {order.get_package_display()}"
    body = "New order received.\n\n" + _order_details(order) + f"\nView in admin: {admin_url}\n"
    return _send(subject, body, order.pk)


def send_payment_confirmed_notification(order: Order) -> bool:
    """Sent exactly once, at the moment an order's status actually
    transitions to PAID (see PaynowService.sync_attempt_status) — not on
    every status poll, and not duplicated between the webhook and htmx
    poll paths, since both funnel through that same transition point."""
    admin_path = reverse("admin:orders_order_change", args=[order.pk])

    next_step = ""
    if order.package == Package.SIGNPOST:
        next_step = (
            f"\nNext step: python manage.py export_signpost_config {order.pk} "
            f"--output client.toml (in the signpost-template repo), fill in "
            f"products, then python generate.py client.toml --zip\n"
        )

    subject = f"Payment received: {order.business_name} \u2014 {order.get_package_display()}"
    body = (
        "Payment confirmed \u2014 time to start building.\n\n"
        + _order_details(order)
        + next_step
        + f"\nView in admin: {admin_path}\n"
    )
    return _send(subject, body, order.pk)
