"""
Generates a pre-filled client.toml skeleton from a Signpost Order — closes
the loop between "payment confirmed" and running the signpost-template
generator. Doesn't know about products/services (the order form doesn't
capture those — see the SOP in phyb-signpost-template/README.md), but
fills everything else so that's the only manual step left.

Usage:
    python manage.py export_signpost_config <order_id>
    python manage.py export_signpost_config <order_id> --output client.toml
"""
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from apps.orders.models import Order, Package


class Command(BaseCommand):
    help = "Export a pre-filled client.toml skeleton for the signpost-template repo from a paid Order."

    def add_arguments(self, parser):
        parser.add_argument("order_id", type=int)
        parser.add_argument(
            "--output", type=str, default=None,
            help="Write to this file instead of stdout (e.g. client.toml)",
        )

    def handle(self, *args, **options):
        try:
            order = Order.objects.get(pk=options["order_id"])
        except Order.DoesNotExist:
            raise CommandError(f"No order with id={options['order_id']}")

        if order.package != Package.SIGNPOST:
            self.stderr.write(self.style.WARNING(
                f"Order #{order.pk} is a {order.get_package_display()}, not Signpost — "
                f"this command is meant for the static-site template, not a Django rebuild. "
                f"Continuing anyway in case that's intentional."
            ))

        if not order.is_paid:
            self.stderr.write(self.style.WARNING(
                f"Order #{order.pk} is not marked PAID yet (status: {order.get_status_display()}) — "
                f"double-check payment actually cleared before delivering."
            ))

        toml_content = self._build_toml(order)

        if options["output"]:
            with open(options["output"], "w", encoding="utf-8") as f:
                f.write(toml_content)
            self.stdout.write(self.style.SUCCESS(f"Written to {options['output']}"))
        else:
            self.stdout.write(toml_content)

    @staticmethod
    def _toml_escape(value: str) -> str:
        """Escape a value for use inside a TOML basic (double-quoted)
        string. Needed because order.notes/business_name/etc. are free
        text a customer typed — a stray quote or newline would otherwise
        produce invalid TOML that tomllib refuses to parse."""
        return value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")

    def _build_toml(self, order: Order) -> str:
        email = order.email or ""
        name = self._toml_escape(order.business_name)
        about = self._toml_escape(order.notes or "")
        phone = self._toml_escape(order.phone)
        email_escaped = self._toml_escape(email)
        address = self._toml_escape(settings.BUSINESS_ADDRESS)

        return f'''# Auto-generated from Order #{order.pk} — fill in products/services below,
# everything else is pre-filled from the order.

[business]
name = "{name}"
tagline = ""  # fill in — not captured by the order form
about = "{about}"

[contact]
whatsapp_number = "{self._normalize_phone(order.phone)}"
phone_display = "{phone}"
email = "{email_escaped}"
address = "{address}"  # defaulted to your address — replace with the CLIENT's location

[brand]
accent_color = "#00bfff"

[footer]
built_by_credit = true

# Fill in the client's real products/services — ask them for a price list
# if it's not already in the order notes above.
[[products]]
name = ""
price = ""
description = ""
'''

    @staticmethod
    def _normalize_phone(phone: str) -> str:
        """Best-effort conversion of a local 07... number to international
        format for the wa.me link — always double-check this manually."""
        digits = "".join(ch for ch in phone if ch.isdigit())
        if digits.startswith("0"):
            return "263" + digits[1:]
        return digits
