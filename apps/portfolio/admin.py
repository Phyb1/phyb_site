from django.contrib import admin

from .models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "client_name", "package", "is_featured", "order", "created_at")
    list_filter = ("package", "is_featured")
    search_fields = ("title", "client_name", "summary")
    prepopulated_fields = {"slug": ("title",)}
    ordering = ("order", "-created_at")
