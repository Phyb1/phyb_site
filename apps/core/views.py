from django.shortcuts import render

from apps.blog.models import Post
from apps.portfolio.models import Project


def home(request):
    context = {
        "featured_projects": Project.objects.filter(is_featured=True)[:3],
        "latest_posts": Post.objects.filter(status=Post.Status.PUBLISHED)[:3],
    }
    return render(request, "core/home.html", context)


def about(request):
    return render(request, "core/about.html")


def pricing(request):
    return render(request, "core/pricing.html")


def error_404(request, exception=None):
    return render(request, "errors/404.html", status=404)


def error_500(request):
    return render(request, "errors/500.html", status=500)
