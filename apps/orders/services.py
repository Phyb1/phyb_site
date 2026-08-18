"""
Thin wrapper around Paynow's API.

Transaction *initiation* (`initiate_web_checkout`/`initiate_mobile_payment`)
is implemented directly here rather than calling the installed `paynow`
package's `send`/`send_mobile` methods — that package (pinned to 1.0.4) has
two confirmed bugs, found by tracing a real production failure:

1. `Paynow.__build`/`__build_mobile` manually URL-encode every field with
   `quote_plus`, then hand the result to `requests.post(data=...)`, which
   URL-encodes the whole dict *again* when building the POST body. Any
   field containing a reserved character — the `://` in resulturl/
   returnurl, an em dash in a package name, spaces — arrives at Paynow
   double-encoded. Paynow decodes once, gets back a still-encoded string,
   and rejects it (observed directly: "ResultUrl must start with http://
   or https://" on a URL that very much did).

2. `InitResponse.__init__` returns early on failure, before the line that
   would set `.error` ever runs — so `.error` can never exist on a failed
   response. Confirmed by reading the source; not a hypothetical.

Status polling (`check_transaction_status`, used below via
`check_status`/`sync_attempt_status`) doesn't hit either bug — it posts an
empty body (nothing to double-encode) and `StatusResponse` has no early
return — so that part of the SDK is still used as-is.

Docs: https://developers.paynow.co.zw/docs/paynow/paynow_api/
Hash spec: https://developers.paynow.co.zw/docs/paynow/generating_hash/
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from urllib.parse import parse_qs

import requests
from django.conf import settings
from paynow import Paynow

from .models import Order, PaymentAttempt

PAYNOW_INITIATE_URL = "https://www.paynow.co.zw/interface/initiatetransaction"
PAYNOW_INITIATE_MOBILE_URL = "https://www.paynow.co.zw/interface/remotetransaction"


def _paynow_hash(fields: dict, integration_key: str) -> str:
    """Concatenate field values (excluding 'hash') in insertion order,
    append the integration key, SHA512, uppercase hex — Paynow's
    documented algorithm, applied to the RAW values (not URL-encoded;
    `requests` handles that once when it serializes the POST body)."""
    concatenated = "".join(str(value) for key, value in fields.items() if key.lower() != "hash")
    concatenated += integration_key
    return hashlib.sha512(concatenated.encode("utf-8")).hexdigest().upper()


def _post_and_parse(url: str, data: dict) -> dict:
    """POST raw (non-pre-encoded) form data and parse Paynow's
    querystring-formatted response into a flat dict."""
    response = requests.post(url, data=data, timeout=15)
    parsed = parse_qs(response.text)
    return {key: values[0] for key, values in parsed.items()}


@dataclass
class InitiateResult:
    success: bool
    poll_url: str = ""
    redirect_url: str = ""
    instructions: str = ""
    error: str = ""


class PaynowService:
    def __init__(self):
        # Still used for status polling (check_status/sync_attempt_status)
        # and to hold the configured credentials/URLs in one place.
        self.client = Paynow(
            settings.PAYNOW_INTEGRATION_ID,
            settings.PAYNOW_INTEGRATION_KEY,
            settings.PAYNOW_RETURN_URL,
            settings.PAYNOW_RESULT_URL,
        )

    def _resolve_authemail(self, order: Order) -> str:
        # PAYNOW_TEST_MODE_EMAIL must win while the integration is in test
        # mode — Paynow rejects any authemail that isn't the merchant's
        # own registered email until the integration is approved live.
        return settings.PAYNOW_TEST_MODE_EMAIL or order.email or settings.CONTACT_EMAIL

    def _base_fields(self, order: Order) -> dict:
        return {
            "resulturl": settings.PAYNOW_RESULT_URL,
            "returnurl": settings.PAYNOW_RETURN_URL,
            "reference": f"PHYB-{order.pk}",
            "amount": str(float(order.amount)),
            "id": settings.PAYNOW_INTEGRATION_ID,
            "additionalinfo": order.get_package_display(),
            "authemail": self._resolve_authemail(order),
        }

    def _handle_initiate_response(
        self, order: Order, data: dict, method: str, instructions_fallback: str = ""
    ) -> InitiateResult:
        status = data.get("status", "")
        success = status.lower() != "error"

        attempt = PaymentAttempt.objects.create(
            order=order,
            method=method,
            reference=data.get("reference", ""),
            poll_url=data.get("pollurl", "") or "",
            raw_response=str(data),
        )

        if not success:
            return InitiateResult(
                success=False,
                error=data.get("error") or status or "Could not start payment.",
            )

        order.status = Order.Status.AWAITING_PAYMENT
        order.save(update_fields=["status", "updated_at"])
        return InitiateResult(
            success=True,
            poll_url=attempt.poll_url,
            redirect_url=data.get("browserurl", ""),
            instructions=data.get("instructions", "") or instructions_fallback,
        )

    def initiate_web_checkout(self, order: Order) -> InitiateResult:
        """Redirect flow — customer pays on Paynow's hosted page (cards,
        or Ecocash/OneMoney entered manually there)."""
        fields = self._base_fields(order)
        fields["status"] = "Message"
        fields["hash"] = _paynow_hash(fields, settings.PAYNOW_INTEGRATION_KEY)

        data = _post_and_parse(PAYNOW_INITIATE_URL, fields)
        return self._handle_initiate_response(order, data, PaymentAttempt.Method.WEB)

    def initiate_mobile_payment(self, order: Order, phone: str, method: str = "ecocash") -> InitiateResult:
        """In-app flow — customer gets a USSD prompt on their phone
        (Ecocash/OneMoney) and enters their PIN there, no redirect."""
        fields = self._base_fields(order)
        fields["phone"] = phone
        fields["method"] = method
        fields["status"] = "Message"
        fields["hash"] = _paynow_hash(fields, settings.PAYNOW_INTEGRATION_KEY)

        data = _post_and_parse(PAYNOW_INITIATE_MOBILE_URL, fields)
        return self._handle_initiate_response(
            order, data, method,
            instructions_fallback="Enter your PIN on the prompt sent to your phone.",
        )

    def check_status(self, poll_url: str) -> str:
        """Returns Paynow's status string, e.g. 'paid', 'created', 'cancelled'.
        Uses the SDK's own method — not affected by either bug above."""
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
