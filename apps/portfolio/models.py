from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Project(models.Model):
    """A past client project shown in the portfolio."""

    class Package(models.TextChoices):
        SIGNPOST = "signpost", "Signpost"
        STARTER = "starter", "Starter"
        PRO = "pro", "Pro"
        CUSTOM = "custom", "Custom build"

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    client_name = models.CharField(max_length=200, blank=True)
    summary = models.CharField(max_length=300, help_text="One-line summary shown on cards.")
    description = models.TextField(blank=True)
    package = models.CharField(max_length=20, choices=Package.choices, default=Package.STARTER)
    live_url = models.URLField(blank=True)
    cover_image = models.ImageField(upload_to="portfolio/covers/", blank=True, null=True)
    is_featured = models.BooleanField(default=False, help_text="Show on the homepage.")
    order = models.PositiveIntegerField(default=0, help_text="Lower numbers appear first.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "-created_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("portfolio:detail", kwargs={"slug": self.slug})
