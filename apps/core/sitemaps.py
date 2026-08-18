from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from apps.blog.models import Post
from apps.portfolio.models import Project


class StaticViewSitemap(Sitemap):
    """Pages with no model behind them — home, about, pricing."""

    priority = 0.8
    changefreq = "weekly"

    def items(self):
        return ["core:home", "core:about", "core:pricing"]

    def location(self, item):
        return reverse(item)


class ProjectSitemap(Sitemap):
    priority = 0.6
    changefreq = "monthly"

    def items(self):
        return Project.objects.all()

    def lastmod(self, obj):
        return obj.updated_at


class PostSitemap(Sitemap):
    priority = 0.6
    changefreq = "monthly"

    def items(self):
        return Post.objects.filter(status=Post.Status.PUBLISHED)

    def lastmod(self, obj):
        return obj.updated_at
