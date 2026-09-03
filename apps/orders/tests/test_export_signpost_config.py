import io

import pytest
from django.core.management import call_command

from apps.orders.models import Order, Package

from .factories import OrderFactory

pytestmark = pytest.mark.django_db


def test_exports_toml_with_business_details():
    order = OrderFactory(
        package=Package.SIGNPOST,
        business_name="Samwa Bakery",
        phone="0776298873",
        status=Order.Status.PAID,
    )
    out = io.StringIO()
    call_command("export_signpost_config", order.pk, stdout=out)

    output = out.getvalue()
    assert 'name = "Samwa Bakery"' in output
    assert 'whatsapp_number = "263776298873"' in output  # normalized from 0776...
    assert 'phone_display = "0776298873"' in output


def test_normalizes_local_phone_to_international():
    order = OrderFactory(package=Package.SIGNPOST, phone="0771234567", status=Order.Status.PAID)
    out = io.StringIO()
    call_command("export_signpost_config", order.pk, stdout=out)
    assert '"263771234567"' in out.getvalue()


def test_unknown_order_id_raises_clear_error():
    from django.core.management.base import CommandError

    with pytest.raises(CommandError):
        call_command("export_signpost_config", 999999)


def test_writes_to_file_when_output_given(tmp_path):
    order = OrderFactory(package=Package.SIGNPOST, status=Order.Status.PAID)
    output_file = tmp_path / "client.toml"
    out = io.StringIO()

    call_command("export_signpost_config", order.pk, "--output", str(output_file), stdout=out)

    assert output_file.exists()
    assert "[business]" in output_file.read_text()


def test_warns_but_does_not_fail_for_non_signpost_package():
    order = OrderFactory(package=Package.BASIC, status=Order.Status.PAID)
    out = io.StringIO()
    err = io.StringIO()

    call_command("export_signpost_config", order.pk, stdout=out, stderr=err)

    assert "not Signpost" in err.getvalue()
    assert "[business]" in out.getvalue()  # still produces output


def test_notes_with_quote_produces_valid_toml():
    """Regression test: order.notes is free text a customer typed — a
    stray quote must not break the generated TOML syntax."""
    import tomllib

    order = OrderFactory(
        package=Package.SIGNPOST,
        notes='Sells "artisan" bread, ask about wholesale',
        status=Order.Status.PAID,
    )
    out = io.StringIO()
    call_command("export_signpost_config", order.pk, stdout=out)

    parsed = tomllib.loads(out.getvalue())  # raises if invalid
    assert "artisan" in parsed["business"]["about"]
