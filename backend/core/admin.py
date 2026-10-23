from django import forms
from pathlib import Path
from django.templatetags.static import static
from django.utils.html import format_html
from django.contrib import admin
from django.db import models
from django.forms import Textarea
from .models import (
    SiteConfig, OverviewSettings, AboutSettings, TechStackSettings,
    ContactSettings, IdentitySettings, Project, Tag, Highlight, KPI,
    Skill, SocialLink, FocusItem, UpdateItem, SKILL_ICON_CHOICES,
)


# Only change the Admin forms, not Tag/Skill model field definitions.
# Updating the model's `choices` would generate an AlterField migration.
_BUNDLED_SKILL_ICONS = Path(__file__).resolve().parent / 'static' / 'core' / 'icons' / 'skills'
_SKILL_ICON_LABELS = {
    'c': 'C', 'cplusplus': 'C++', 'csharp': 'C#', 'cmake': 'CMake',
    'css3': 'CSS3', 'fastapi': 'FastAPI', 'flask': 'Flask',
    'github': 'GitHub', 'gitlab': 'GitLab', 'grafana': 'Grafana',
    'html5': 'HTML5', 'java': 'Java', 'jupyter': 'Jupyter',
    'keras': 'Keras', 'matplotlib': 'Matplotlib', 'maven': 'Maven',
    'mongodb': 'MongoDB', 'mysql': 'MySQL', 'nextjs': 'Next.js',
    'nginx': 'Nginx', 'numpy': 'NumPy', 'opencv': 'OpenCV',
    'pandas': 'pandas', 'prometheus': 'Prometheus', 'pytest': 'pytest',
    'redis': 'Redis', 'rust': 'Rust', 'scikitlearn': 'scikit-learn',
    'spring': 'Spring Boot', 'sqlite': 'SQLite',
    'tensorflow': 'TensorFlow', 'unity': 'Unity', 'vercel': 'Vercel',
    'vitejs': 'Vite',
    'kotlin': 'Kotlin', 'kvmqemu': 'KVM/QEMU', 'lz4': 'LZ4',
    'mcp': 'MCP', 's3': 'Amazon S3', 'websocket': 'WebSocket',
}


def _admin_skill_icon_choices():
    """Present every shipped technology SVG without modifying model choices."""
    labels = dict(SKILL_ICON_CHOICES[1:])
    for path in _BUNDLED_SKILL_ICONS.glob('*.svg'):
        key = path.stem
        if len(key) <= 24:  # Tag.icon_key and Skill.icon_key max_length
            labels[key] = _SKILL_ICON_LABELS.get(key, labels.get(key, key.replace('-', ' ').title()))
    return [('', 'Automatic by name / uploaded icon'), *sorted(labels.items(), key=lambda row: row[1].casefold())]


class TechnologyIconAdminForm(forms.ModelForm):
    icon_key = forms.ChoiceField(required=False, choices=())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        choices = _admin_skill_icon_choices()
        current = getattr(self.instance, 'icon_key', '')
        if current and current not in {value for value, _ in choices}:
            choices.append((current, f'{current} (previously selected)'))
        self.fields['icon_key'].choices = choices
        self.fields['icon_key'].help_text = (
            'Choose a bundled technology logo, or leave blank to use an '
            'uploaded image or automatically match the technology name.'
        )

    def _get_validation_exclusions(self):
        excluded = super()._get_validation_exclusions()
        # The model keeps its historical choices (no migration), while the
        # Admin form validates selections against actual bundled SVG filenames.
        excluded.add('icon_key')
        return excluded


class TagTechnologyIconForm(TechnologyIconAdminForm):
    class Meta:
        model = Tag
        fields = '__all__'


class SkillTechnologyIconForm(TechnologyIconAdminForm):
    class Meta:
        model = Skill
        fields = '__all__'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    form = TagTechnologyIconForm
    list_display = ('name', 'slug', 'icon_key')
    search_fields = ('name',)
    # Let Tag.save() generate safe slugs for C, C++ and C#; Django's JS
    # prepopulation collapses all three to 'c'.
    prepopulated_fields = {}


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
    verbose_name_plural = 'About · Highlights (achievements, not technologies)'
    extra = 0
    ordering = ('order',)


class KPIInline(admin.TabularInline):
    model = KPI
    verbose_name_plural = 'Overview · KPIs'
    extra = 0
    ordering = ('order',)


class SkillInline(admin.TabularInline):
    verbose_name_plural = 'Tech Stack · Technologies'
    form = SkillTechnologyIconForm
    model = Skill
    extra = 0
    ordering = ('order',)
    fields = ('name', 'icon_key', 'icon_image', 'order', 'is_visible')


class SocialLinkInline(admin.TabularInline):
    model = SocialLink
    verbose_name_plural = 'Contact & Links · Social links'
    extra = 0
    ordering = ('order',)
    fields = ('platform', 'label', 'url', 'placement', 'order', 'is_visible')


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


class PageSettingsAdmin(admin.ModelAdmin):
    """Each admin page edits the same underlying SiteConfig row."""
    list_display = ('display_name', 'updated_at')
    list_per_page = 25

    def has_add_permission(self, request):
        # Only Identity can create the shared configuration; never create duplicates.
        return self.model is IdentitySettings and not SiteConfig.objects.exists()

    @admin.display(description='Profile')
    def display_name(self, obj):
        return obj.full_name


@admin.register(OverviewSettings)
class OverviewSettingsAdmin(PageSettingsAdmin):
    fieldsets = (
        ('Overview · Introduction', {'fields': ('hero_title', 'overview_description')}),
    )
    inlines = (FocusItemInline, UpdateItemInline, KPIInline)


@admin.register(AboutSettings)
class AboutSettingsAdmin(PageSettingsAdmin):
    fieldsets = (
        ('About · Profile', {'fields': ('headline', 'bio'),
                             'description': 'The biography accepts Markdown.'}),
    )
    inlines = (HighlightInline,)


@admin.register(TechStackSettings)
class TechStackSettingsAdmin(PageSettingsAdmin):
    fieldsets = (
        ('Tech Stack · Introduction', {'fields': ('tech_stack_intro',)}),
    )
    inlines = (SkillInline,)


@admin.register(ContactSettings)
class ContactSettingsAdmin(PageSettingsAdmin):
    fieldsets = (
        ('Contact & Links · Destinations', {'fields': ('email', 'github_url', 'cv_file'),
          'description': "Each social link explicitly chooses Let's Connect or Links."}),
    )
    inlines = (SocialLinkInline,)


@admin.register(IdentitySettings)
class IdentitySettingsAdmin(PageSettingsAdmin):
    readonly_fields = ('display_full_name',)
    fieldsets = (
        ('Identity · Site-wide', {'fields': ('first_name', 'last_name', 'display_full_name', 'avatar'),
          'description': 'Full name is computed from First name and Last name. '
                         'These names are also used by Job Matching PDF filenames.'}),
    )

    @admin.display(description='Full name (automatic)')
    def display_full_name(self, obj):
        if not obj.pk:
            return 'Calculated upon saving'
        return obj.full_name
