from django.contrib import admin

from .models import Order, PaymentAttempt


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


@admin.register(PaymentAttempt)
class PaymentAttemptAdmin(admin.ModelAdmin):
    list_display = ("order", "method", "paynow_status", "created_at")
    list_filter = ("method", "paynow_status")
    readonly_fields = ("order", "method", "reference", "poll_url", "raw_response", "created_at", "updated_at")
