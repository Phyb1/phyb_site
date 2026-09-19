import io

import pytest
from django.core.management import call_command

from apps.blog.models import Post

pytestmark = pytest.mark.django_db


def test_creates_three_posts():
    call_command("seed_local_seo_posts", stdout=io.StringIO())
    assert Post.objects.count() == 3


def test_rerunning_updates_rather_than_duplicates():
    call_command("seed_local_seo_posts", stdout=io.StringIO())
    call_command("seed_local_seo_posts", stdout=io.StringIO())
    assert Post.objects.count() == 3


def test_posts_use_consistent_cta_keyword():
    call_command("seed_local_seo_posts", stdout=io.StringIO())
    for post in Post.objects.all():
        assert '"SIGNPOST"' in post.body
        assert '"WEBSITE"' not in post.body


def test_coexists_with_first_batch_without_slug_collision():
    call_command("seed_launch_posts", stdout=io.StringIO())
    call_command("seed_local_seo_posts", stdout=io.StringIO())
    assert Post.objects.count() == 6
