from django.contrib import admin
from .models import SiteConfig, Tag, Project


@admin.register(SiteConfig)
class SiteConfigAdmin(admin.ModelAdmin):
    list_display = ("full_name", "headline", "email", "updated_at")


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "is_featured", "order", "updated_at")
    list_filter = ("is_featured", "tags")
    search_fields = ("title", "summary", "description")
    ordering = ("order", "-created_at")
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("tags",)
