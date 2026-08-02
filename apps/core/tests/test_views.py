import pytest
from django.urls import reverse


pytestmark = pytest.mark.django_db


def test_home_returns_200(client):
    response = client.get(reverse("core:home"))
    assert response.status_code == 200


def test_about_returns_200(client):
    response = client.get(reverse("core:about"))
    assert response.status_code == 200


def test_pricing_returns_200(client):
    response = client.get(reverse("core:pricing"))
    assert response.status_code == 200


def test_pricing_shows_signpost_price(client):
    response = client.get(reverse("core:pricing"))
    assert b"25" in response.content


def test_pricing_shows_all_three_packages(client):
    response = client.get(reverse("core:pricing"))
    assert b"Signpost" in response.content
    assert b"Starter" in response.content
    assert b"Pro" in response.content


def test_pricing_shows_addons_and_payment_terms(client):
    response = client.get(reverse("core:pricing"))
    assert b"$120" in response.content  # blog/CMS add-on
    assert b"Payment terms" in response.content
    assert b"Timeline" in response.content


def test_whatsapp_fab_present_on_every_page(client):
    response = client.get(reverse("core:home"))
    assert b"whatsapp-fab" in response.content


def test_whatsapp_link_uses_configured_number(client, settings):
    settings.WHATSAPP_NUMBER = "263700000000"
    response = client.get(reverse("core:home"))
    assert b"https://wa.me/263700000000" in response.content


def test_footer_contact_links_present(client):
    response = client.get(reverse("core:home"))
    assert b"footer-links" in response.content
    assert b"mailto:" in response.content


def test_theme_toggle_present(client):
    response = client.get(reverse("core:home"))
    assert b"theme-toggle" in response.content


def test_no_bootstrap_cdn_reference(client):
    response = client.get(reverse("core:home"))
    assert b"cdn.jsdelivr" not in response.content
    assert b"bootstrap" not in response.content.lower()


def test_home_copy_does_not_mention_django(client):
    response = client.get(reverse("core:home"))
    assert b"django" not in response.content.lower()


def test_about_copy_does_not_mention_django(client):
    response = client.get(reverse("core:about"))
    assert b"django" not in response.content.lower()
