import pytest

from .factories import PostFactory

pytestmark = pytest.mark.django_db


def test_slug_auto_generated_from_title():
    post = PostFactory(title="How To Get Found On Google", slug="")
    assert post.slug == "how-to-get-found-on-google"


def test_str_returns_title():
    post = PostFactory(title="Why Every Business Needs A Signpost")
    assert str(post) == "Why Every Business Needs A Signpost"
