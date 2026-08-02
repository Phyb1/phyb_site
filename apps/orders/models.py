from decimal import Decimal

from django.db import models
from django.urls import reverse


class Package(models.TextChoices):
    SIGNPOST = "signpost", "2-Page Signpost — $25/year"
    STARTER = "starter", "Starter — $280"
    PRO = "pro", "Pro — $480"
    CUSTOM = "custom", "Custom quote"


PACKAGE_PRICES = {
    Package.SIGNPOST: Decimal("25.00"),
    Package.STARTER: Decimal("280.00"),
    Package.PRO: Decimal("480.00"),
    Package.CUSTOM: Decimal("0.00"),
}


class Order(models.Model):
    """A lead / order for a website package. Created as soon as someone
    submits the request form, before any payment happens — this is the
    source of truth for the sales pipeline, not just paid orders."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending payment"
        AWAITING_PAYMENT = "awaiting_payment", "Awaiting payment"
        PAID = "paid", "Paid"
        FAILED = "failed", "Payment failed"
        CANCELLED = "cancelled", "Cancelled"

    package = models.CharField(max_length=20, choices=Package.choices, default=Package.SIGNPOST)
    business_name = models.CharField(max_length=200)
    contact_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20, help_text="WhatsApp number, e.g. 0776298873")
    email = models.EmailField(blank=True)
    notes = models.TextField(blank=True, help_text="What the business sells, existing socials, etc.")

    amount = models.DecimalField(max_digits=8, decimal_places=2, editable=False)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.business_name} — {self.get_package_display()}"

    def save(self, *args, **kwargs):
        if not self.amount:
            self.amount = PACKAGE_PRICES[self.package]
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("orders:status", kwargs={"pk": self.pk})

    @property
    def is_paid(self):
        return self.status == self.Status.PAID


class PaymentAttempt(models.Model):
    """One Paynow transaction attempt against an Order. Kept separate from
    Order so retries don't destroy history — useful for support/debugging
    when a customer says 'I paid but it still shows pending'."""

    class Method(models.TextChoices):
        ECOCASH = "ecocash", "Ecocash"
        ONEMONEY = "onemoney", "OneMoney"
        WEB = "web", "Paynow web checkout"

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="payment_attempts")
    method = models.CharField(max_length=20, choices=Method.choices)
    reference = models.CharField(max_length=100, blank=True)
    poll_url = models.URLField(blank=True)
    paynow_status = models.CharField(max_length=50, blank=True)
    raw_response = models.TextField(blank=True, help_text="Last raw status response, for debugging.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.order} — {self.method} ({self.paynow_status or 'pending'})"
