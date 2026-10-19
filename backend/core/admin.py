from django import forms
from django.templatetags.static import static
from django.utils.html import format_html
from django.contrib import admin
from django.db import models
from django.forms import Textarea
from .models import SiteConfig, Project, Tag, Highlight, KPI, Skill, SocialLink, FocusItem, UpdateItem


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'icon_key')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


class ProjectIconPickerForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = '__all__'
        widgets = {
            'icon_key': forms.Select(attrs={
                'data-project-icon-picker': '1',
                'data-icon-sprite': static('core/icons/ui.svg'),
            }),
        }


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    form = ProjectIconPickerForm
    list_display = ('title', 'icon_preview', 'icon_key', 'is_featured', 'order', 'updated_at')
    list_editable = ('is_featured', 'order')
    list_filter = ('is_featured', 'tags')
    search_fields = ('title', 'summary', 'description')
    ordering = ('order', '-created_at')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('tags',)
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={
            'rows': 18, 'style': 'font-family: ui-monospace, monospace;'
        })}
    }

    @admin.display(description='Icon')
    def icon_preview(self, obj):
        return format_html(
            '<svg aria-hidden="true" width="21" height="21" '
            'style="color:var(--body-fg);vertical-align:middle">'
            '<use href="{}#{}"></use></svg>',
            static('core/icons/ui.svg'), obj.icon_key or 'package',
        )

    class Media:
        css = {'all': ('core/admin/project_icon_picker.css',)}
        js = ('core/admin/project_icon_picker.js',)


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


class SocialLinkInline(admin.TabularInline):
    model = SocialLink
    extra = 0
    ordering = ('order',)
    fields = ('platform', 'label', 'url', 'order', 'is_visible')


class FocusItemInline(admin.TabularInline):
    model = FocusItem
    extra = 0
    ordering = ('order', 'id')
    fields = ('title', 'description', 'status', 'order', 'is_visible')
    verbose_name_plural = 'Overview · Current focus (manual)'


class UpdateItemInline(admin.StackedInline):
    model = UpdateItem
    extra = 0
    ordering = ('-published_at', '-id')
    fields = ('title', 'summary', 'published_at', 'url', 'is_visible')
    verbose_name_plural = 'Overview · Recent updates (manual)'


@admin.register(SiteConfig)
class SiteConfigAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'headline', 'updated_at')
    fieldsets = (
        ('Identity', {'fields': ('full_name', 'headline', 'avatar')}),
        ('Home page', {'fields': ('hero_title', 'overview_description', 'intro', 'bio', 'resume_intro'),
                       'description': 'Only configured text appears on the website. The biography accepts Markdown.'}),
        ('Links', {'fields': ('email', 'github_url', 'cv_file')}),
    )
    inlines = (FocusItemInline, UpdateItemInline, SkillInline, SocialLinkInline, HighlightInline, KPIInline)
