import pytest
from django.urls import reverse

from .factories import PostFactory
from apps.blog.models import Post

pytestmark = pytest.mark.django_db


def test_list_shows_only_published_posts(client):
    PostFactory(title="Published Post", status=Post.Status.PUBLISHED)
    PostFactory(title="Draft Post", status=Post.Status.DRAFT)

    response = client.get(reverse("blog:list"))

    assert b"Published Post" in response.content
    assert b"Draft Post" not in response.content


def test_draft_post_detail_returns_404(client):
    post = PostFactory(status=Post.Status.DRAFT)
    response = client.get(post.get_absolute_url())
    assert response.status_code == 404


def test_published_post_detail_returns_200(client):
    post = PostFactory(status=Post.Status.PUBLISHED)
    response = client.get(post.get_absolute_url())
    assert response.status_code == 200
