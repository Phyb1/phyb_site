from django.contrib import admin

from .models import Order, PaymentAttempt
from .notifications import send_payment_confirmed_notification


class PaymentAttemptInline(admin.TabularInline):
    model = PaymentAttempt
    extra = 0
    readonly_fields = ("method", "reference", "poll_url", "paynow_status", "created_at")
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("business_name", "package", "amount", "status", "phone", "created_at")
    list_filter = ("package", "status")
    search_fields = ("business_name", "contact_name", "phone", "email")
    readonly_fields = ("amount", "created_at", "updated_at")
    inlines = [PaymentAttemptInline]

    def save_model(self, request, obj, form, change):
        """Direct EcoCash transfers have no webhook \u2014 the only way an
        order becomes PAID for that flow is a manual status change here.
        Fire the same payment-confirmed email Paynow's webhook path
        triggers, guarded the same way (only on the actual transition, so
        re-saving an already-PAID order doesn't resend it)."""
        was_paid = False
        if change and obj.pk:
            was_paid = Order.objects.filter(pk=obj.pk, status=Order.Status.PAID).exists()

        super().save_model(request, obj, form, change)

        if obj.status == Order.Status.PAID and not was_paid:
            send_payment_confirmed_notification(obj)


@admin.register(PaymentAttempt)
class PaymentAttemptAdmin(admin.ModelAdmin):
    list_display = ("order", "method", "paynow_status", "created_at")
    list_filter = ("method", "paynow_status")
    readonly_fields = ("order", "method", "reference", "poll_url", "raw_response", "created_at", "updated_at")
