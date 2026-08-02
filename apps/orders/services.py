"""
Thin wrapper around the `paynow` package.

Kept as a separate service class (rather than calling `paynow` directly from
views) for two reasons:
1. Views/tests depend on PaynowService, which is easy to mock — no real
   network calls needed in the test suite.
2. If Paynow's SDK changes, only this file needs to change.

Docs: https://developers.paynow.co.zw/docs/intro.html
"""
from __future__ import annotations

from dataclasses import dataclass

from django.conf import settings
from paynow import Paynow

from .models import Order, PaymentAttempt


@dataclass
class InitiateResult:
    success: bool
    poll_url: str = ""
    redirect_url: str = ""
    instructions: str = ""
    error: str = ""


class PaynowService:
    def __init__(self):
        self.client = Paynow(
            settings.PAYNOW_INTEGRATION_ID,
            settings.PAYNOW_INTEGRATION_KEY,
            settings.PAYNOW_RETURN_URL,
            settings.PAYNOW_RESULT_URL,
        )

    def _build_payment(self, order: Order):
        reference = f"PHYB-{order.pk}"
        payment = self.client.create_payment(reference, order.email or "billing@phyb.co.zw")
        payment.add(order.get_package_display(), float(order.amount))
        return payment

    def initiate_web_checkout(self, order: Order) -> InitiateResult:
        """Redirect flow — customer pays on Paynow's hosted page (cards,
        or Ecocash/OneMoney entered manually there)."""
        payment = self._build_payment(order)
        response = self.client.send(payment)

        attempt = PaymentAttempt.objects.create(
            order=order,
            method=PaymentAttempt.Method.WEB,
            reference=getattr(response, "reference", ""),
            poll_url=getattr(response, "poll_url", "") or "",
            raw_response=str(getattr(response, "data", "")),
        )

        if response.success:
            order.status = Order.Status.AWAITING_PAYMENT
            order.save(update_fields=["status", "updated_at"])
            return InitiateResult(
                success=True,
                poll_url=attempt.poll_url,
                redirect_url=response.redirect_url,
            )
        return InitiateResult(success=False, error=response.error or "Could not start payment.")

    def initiate_mobile_payment(self, order: Order, phone: str, method: str = "ecocash") -> InitiateResult:
        """In-app flow — customer gets a USSD prompt on their phone
        (Ecocash/OneMoney) and enters their PIN there, no redirect."""
        payment = self._build_payment(order)
        response = self.client.send_mobile(payment, phone, method)

        attempt = PaymentAttempt.objects.create(
            order=order,
            method=method,
            reference=getattr(response, "reference", ""),
            poll_url=getattr(response, "poll_url", "") or "",
            raw_response=str(getattr(response, "data", "")),
        )

        if response.success:
            order.status = Order.Status.AWAITING_PAYMENT
            order.save(update_fields=["status", "updated_at"])
            return InitiateResult(
                success=True,
                poll_url=attempt.poll_url,
                instructions=getattr(response, "instructions", "") or "Enter your PIN on the prompt sent to your phone.",
            )
        return InitiateResult(success=False, error=response.error or "Could not start mobile payment.")

    def check_status(self, poll_url: str) -> str:
        """Returns Paynow's status string, e.g. 'paid', 'created', 'cancelled'."""
        status_response = self.client.check_transaction_status(poll_url)
        return (status_response.status or "").lower()

    def sync_attempt_status(self, attempt: PaymentAttempt) -> PaymentAttempt:
        """Poll Paynow for the latest status and update our own records to
        match. Used both by the webhook and by the htmx status-poll view."""
        if not attempt.poll_url:
            return attempt

        status = self.check_status(attempt.poll_url)
        attempt.paynow_status = status
        attempt.save(update_fields=["paynow_status", "updated_at"])

        order = attempt.order
        if status == "paid" and order.status != Order.Status.PAID:
            order.status = Order.Status.PAID
            order.save(update_fields=["status", "updated_at"])
        elif status in {"cancelled", "disputed"}:
            order.status = Order.Status.CANCELLED
            order.save(update_fields=["status", "updated_at"])
        elif status == "failed":
            order.status = Order.Status.FAILED
            order.save(update_fields=["status", "updated_at"])

        return attempt
