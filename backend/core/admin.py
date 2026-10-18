from django.contrib import admin
from django.db import models
from django.forms import Textarea
from .models import SiteConfig, Project, Tag, Highlight, KPI, Skill


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'icon_key')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'icon_key', 'is_featured', 'order', 'updated_at')
    list_editable = ('is_featured', 'order')
    list_filter = ('is_featured', 'tags')
    search_fields = ('title', 'summary', 'description')
    ordering = ('order', '-created_at')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('tags',)
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 18, 'style': 'font-family: ui-monospace, monospace;'})}
    }


class HighlightInline(admin.TabularInline):
    model = Highlight
    extra = 0
    ordering = ('order',)


class KPIInline(admin.TabularInline):
    model = KPI
    extra = 0
    ordering = ('order',)


class SkillInline(admin.TabularInline):
    model = Skill
    extra = 0
    ordering = ('order',)
    fields = ('name', 'icon_key', 'icon_image', 'order', 'is_visible')


@admin.register(SiteConfig)
class SiteConfigAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'headline', 'updated_at')
    fieldsets = (
        ('Identity', {'fields': ('full_name', 'headline', 'avatar')}),
        ('Home page', {'fields': ('hero_title', 'intro', 'bio', 'resume_intro'),
                       'description': 'Only configured text appears on the website. The biography accepts Markdown.'}),
        ('Links', {'fields': ('email', 'github_url', 'cv_file')}),
    )
    inlines = (SkillInline, HighlightInline, KPIInline)
