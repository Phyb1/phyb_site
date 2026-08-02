import pytest
from django.urls import reverse

from .factories import ProjectFactory

pytestmark = pytest.mark.django_db


def test_project_list_returns_200(client):
    ProjectFactory()
    response = client.get(reverse("portfolio:list"))
    assert response.status_code == 200


def test_project_list_shows_project_title(client):
    project = ProjectFactory(title="Samwa Bakery")
    response = client.get(reverse("portfolio:list"))
    assert project.title.encode() in response.content


def test_project_detail_returns_200(client):
    project = ProjectFactory()
    response = client.get(project.get_absolute_url())
    assert response.status_code == 200


def test_project_detail_404_for_unknown_slug(client):
    response = client.get(reverse("portfolio:detail", kwargs={"slug": "does-not-exist"}))
    assert response.status_code == 404
