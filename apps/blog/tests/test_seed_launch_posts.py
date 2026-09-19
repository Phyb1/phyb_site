import io

import pytest
from django.core.management import call_command

from apps.blog.models import Post

pytestmark = pytest.mark.django_db


def test_creates_three_posts():
    call_command("seed_launch_posts", stdout=io.StringIO())
    assert Post.objects.count() == 3


def test_defaults_to_published():
    call_command("seed_launch_posts", stdout=io.StringIO())
    assert Post.objects.filter(status=Post.Status.PUBLISHED).count() == 3


def test_status_draft_flag_sets_draft():
    call_command("seed_launch_posts", "--status", "draft", stdout=io.StringIO())
    assert Post.objects.filter(status=Post.Status.DRAFT).count() == 3


def test_rerunning_updates_rather_than_duplicates():
    call_command("seed_launch_posts", stdout=io.StringIO())
    call_command("seed_launch_posts", stdout=io.StringIO())
    assert Post.objects.count() == 3


def test_posts_have_working_slugs_and_urls():
    call_command("seed_launch_posts", stdout=io.StringIO())
    post = Post.objects.get(slug="how-much-should-a-website-cost-in-zimbabwe")
    assert post.get_absolute_url() == "/blog/how-much-should-a-website-cost-in-zimbabwe/"


def test_posts_mention_pricing_cta():
    call_command("seed_launch_posts", stdout=io.StringIO())
    for post in Post.objects.all():
        assert "phyb.co.zw/pricing" in post.body


def test_posts_use_current_page_counts_and_renewal_price():
    """Regression guard: this batch was written before the pricing page's
    page counts and renewal price changed (4/7 pages, ~$45/yr renewal) —
    confirms the seeded copy was updated to match, not left stale."""
    call_command("seed_launch_posts", stdout=io.StringIO())
    cost_post = Post.objects.get(slug="how-much-should-a-website-cost-in-zimbabwe")
    assert "up to 5 pages" in cost_post.body
    assert "up to 8 pages" in cost_post.body
    assert "roughly $45" not in cost_post.body
