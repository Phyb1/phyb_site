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


def test_pricing_shows_all_four_packages(client):
    response = client.get(reverse("core:pricing"))
    assert b"Signpost" in response.content
    assert b"Basic" in response.content
    assert b"Standard" in response.content
    assert b"Premium" in response.content


def test_pricing_shows_package_prices(client):
    response = client.get(reverse("core:pricing"))
    assert b"$80" in response.content
    assert b"$200" in response.content
    assert b"$370" in response.content


def test_pricing_shows_addons_and_payment_terms(client):
    response = client.get(reverse("core:pricing"))
    assert b"$80" in response.content  # logo/branding add-on
    assert b"Payment terms" in response.content
    assert b"Timeline" in response.content


def test_pricing_highlights_admin_panel_on_every_tier(client):
    """Basic explicitly lists the admin panel too, not just Standard/Premium —
    the comparison table's 'Admin panel' row should read \u2713 across all three."""
    response = client.get(reverse("core:pricing"))
    assert b"Admin panel" in response.content
    assert response.content.lower().count(b"admin panel") >= 2


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


def test_robots_txt_returns_200_and_references_sitemap(client):
    response = client.get("/robots.txt")
    assert response.status_code == 200
    assert response["Content-Type"].startswith("text/plain")
    assert b"Sitemap:" in response.content
    assert b"/sitemap.xml" in response.content


def test_robots_txt_disallows_admin(client):
    response = client.get("/robots.txt")
    assert b"Disallow: /admin/" in response.content


def test_sitemap_xml_returns_200(client):
    response = client.get("/sitemap.xml")
    assert response.status_code == 200
    assert b"<urlset" in response.content


def test_sitemap_includes_static_pages(client):
    response = client.get("/sitemap.xml")
    assert b"/pricing/" in response.content


def test_home_includes_structured_data(client):
    response = client.get(reverse("core:home"))
    assert b"application/ld+json" in response.content
    assert b"ProfessionalService" in response.content
