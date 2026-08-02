import pytest

from .factories import ProjectFactory

pytestmark = pytest.mark.django_db


def test_slug_auto_generated_from_title():
    project = ProjectFactory(title="Samwa Bakery", slug="")
    assert project.slug == "samwa-bakery"


def test_str_returns_title():
    project = ProjectFactory(title="Shato Sports Bar")
    assert str(project) == "Shato Sports Bar"


def test_get_absolute_url():
    project = ProjectFactory(title="KurudzArt")
    assert project.get_absolute_url() == f"/portfolio/{project.slug}/"
