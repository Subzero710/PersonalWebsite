from django.db import models
from django.utils.text import slugify
from django.utils import timezone

# Icon values select visual assets, never project/skill content.
ICON_CHOICES = [
    ('', 'No icon'),
    ('General', [
        ('package', 'Package / cube'),
        ('layers', 'Layers'),
        ('settings', 'Settings'),
        ('folder-open', 'Files / folder'),
        ('target', 'Target / focus'),
        ('activity', 'Activity'),
        ('badge-check', 'Verified'),
        ('sparkles', 'Sparkles'),
        ('bell', 'Notifications'),
        ('archive', 'Archive'),
        ('timer', 'Timer'),
        ('alarm-clock', 'Alarm'),
        ('calendar-days', 'Calendar'),
        ('calendar-check', 'Scheduled'),
        ('check-check', 'Completed'),
        ('briefcase-business', 'Business'),
        ('graduation-cap', 'Education'),
    ]),
    ('Web & applications', [
        ('code', 'Code / brackets'),
        ('globe', 'Website / globe'),
        ('terminal', 'Terminal'),
        ('monitor', 'Desktop application'),
        ('smartphone', 'Mobile application'),
        ('laptop', 'Laptop'),
        ('layout-dashboard', 'Dashboard'),
        ('kanban', 'Kanban board'),
        ('columns', 'Columns / dashboard'),
        ('chat', 'Chat / conversation'),
        ('message-square', 'Messages'),
        ('users', 'Collaboration / users'),
        ('braces', 'Code / curly braces'),
        ('blocks', 'Components'),
        ('camera', 'Camera'),
        ('image', 'Image'),
        ('video', 'Video'),
        ('mic', 'Microphone'),
        ('audio-lines', 'Audio waveform'),
        ('webcam', 'Webcam'),
        ('notebook-tabs', 'Notebook'),
        ('notebook-pen', 'Notes / writing'),
    ]),
    ('Data & analytics', [
        ('database', 'Database'),
        ('chart', 'Analytics / chart'),
        ('chart-no-axes-column', 'Bar chart'),
        ('chart-pie', 'Pie chart'),
        ('table', 'Data table'),
        ('database-zap', 'Database operations'),
        ('hard-drive', 'Storage'),
        ('binary', 'Binary / low-level'),
        ('search-code', 'Code search'),
        ('qr-code', 'QR code'),
        ('clipboard-list', 'Checklist / records'),
    ]),
    ('Cloud & DevOps', [
        ('cloud', 'Cloud'),
        ('server', 'Server'),
        ('network', 'Network'),
        ('cpu', 'Hardware / compute'),
        ('rocket', 'Deployment'),
        ('workflow', 'Workflow'),
        ('git-branch', 'Git branches'),
        ('cloud-cog', 'Cloud configuration'),
        ('cloud-upload', 'Cloud upload'),
        ('container', 'Container / Docker'),
        ('git-commit-horizontal', 'Git commit'),
        ('git-pull-request', 'Pull request'),
        ('server-cog', 'Server configuration'),
        ('wifi', 'Wireless network'),
        ('radio-tower', 'Radio / signal'),
        ('webhook', 'Webhook'),
        ('plug', 'Integration / plug'),
        ('route', 'Routing'),
        ('folder-git-2', 'Git repository'),
    ]),
    ('Security', [
        ('shield', 'Security'),
        ('lock', 'Authentication / lock'),
        ('bug', 'Bug / testing'),
        ('shield-check', 'Secured / verified'),
        ('lock-keyhole', 'Access control'),
        ('file-lock', 'Protected file'),
        ('scan-eye', 'Inspection'),
        ('key-round', 'Credentials / key'),
        ('fingerprint-pattern', 'Fingerprint / identity'),
    ]),
    ('Other tools', [
        ('api', 'API / integration'),
        ('bot', 'Automation / bot'),
        ('brain-circuit', 'AI / machine learning'),
        ('puzzle', 'Plugin'),
        ('list-todo', 'Task list'),
        ('flask-conical', 'Experiment / research'),
        ('map-pin', 'Location'),
        ('shopping-cart', 'Shopping'),
        ('wallet', 'Payments / wallet'),
        ('zap', 'Performance / energy'),
        ('files', 'Multiple files'),
        ('gamepad', 'Game'),
        ('wrench', 'Tools'),
        ('book-open', 'Documentation'),
    ]),
]

SOCIAL_PLATFORM_CHOICES = [
    ('github', 'GitHub'), ('linkedin', 'LinkedIn'), ('gitlab', 'GitLab'),
    ('x', 'X / Twitter'), ('bluesky', 'Bluesky'), ('mastodon', 'Mastodon'),
    ('discord', 'Discord'), ('youtube', 'YouTube'), ('instagram', 'Instagram'),
    ('reddit', 'Reddit'), ('stackoverflow', 'Stack Overflow'),
    ('devto', 'DEV Community'), ('medium', 'Medium'), ('twitch', 'Twitch'),
    ('website', 'Personal website'), ('globe', 'Other website'),
]
SKILL_ICON_CHOICES = [
    ('', 'Use uploaded icon / text only'),
    ('python', 'Python'), ('go', 'Go'), ('typescript', 'TypeScript'),
    ('docker', 'Docker'), ('terraform', 'Terraform'), ('aws', 'AWS'),
    ('postgresql', 'PostgreSQL'), ('linux', 'Linux'), ('bash', 'Bash'),
    ('django', 'Django'), ('git', 'Git'), ('kubernetes', 'Kubernetes'),
    ('javascript', 'JavaScript'), ('react', 'React'), ('nodejs', 'Node.js'),
]


class SiteConfig(models.Model):
    full_name = models.CharField(max_length=120)
    first_name = models.CharField(max_length=80, blank=True, help_text="Used for Job Matching PDF filename: last_first_role.pdf.")
    last_name = models.CharField(max_length=80, blank=True, help_text="Used for Job Matching PDF filename: last_first_role.pdf.")
    headline = models.CharField(max_length=200, blank=True)
    hero_title = models.CharField(max_length=180, blank=True)
    overview_description = models.TextField(
        blank=True,
        help_text='A short introduction to this website, distinct from the personal biography.',
    )
    intro = models.TextField(blank=True)
    bio = models.TextField(blank=True, help_text='Markdown supported.')
    resume_intro = models.TextField(blank=True)
    email = models.EmailField(blank=True)
    github_url = models.URLField(blank=True)
    cv_file = models.FileField(upload_to='cv/', blank=True, null=True)
    avatar = models.ImageField(upload_to='avatar/', blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.full_name


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=80, unique=True, blank=True)
    icon_key = models.CharField(max_length=24, blank=True, choices=SKILL_ICON_CHOICES)
    icon_image = models.ImageField(upload_to='tag-icons/', blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            special_slugs = {'c++': 'cplusplus', 'c#': 'csharp'}
            self.slug = special_slugs.get(self.name.strip().casefold(), slugify(self.name))[:80]
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Project(models.Model):
    title = models.CharField(max_length=140)
    slug = models.SlugField(max_length=180, unique=True, blank=True)
    summary = models.CharField(max_length=240, blank=True)
    description = models.TextField(blank=True)
    tags = models.ManyToManyField(Tag, blank=True, related_name='projects')
    repo_url = models.URLField(blank=True)
    demo_url = models.URLField(blank=True)
    icon_key = models.CharField(max_length=32, blank=True, choices=ICON_CHOICES)
    is_featured = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', '-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:180]
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Highlight(models.Model):
    site = models.ForeignKey('SiteConfig', related_name='highlights', on_delete=models.CASCADE)
    text = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return self.text


class KPI(models.Model):
    site = models.ForeignKey('SiteConfig', related_name='kpis', on_delete=models.CASCADE)
    value = models.CharField(max_length=32)
    label = models.CharField(max_length=32)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f'{self.value} — {self.label}'


class Skill(models.Model):
    site = models.ForeignKey('SiteConfig', related_name='skills', on_delete=models.CASCADE)
    name = models.CharField(max_length=80)
    icon_key = models.CharField(max_length=24, blank=True, choices=SKILL_ICON_CHOICES)
    icon_image = models.ImageField(upload_to='skill-icons/', blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    is_visible = models.BooleanField(default=True)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return self.name


class SocialLink(models.Model):
    """User-configured public contact destinations, attached to SiteConfig."""
    site = models.ForeignKey(SiteConfig, related_name='social_links', on_delete=models.CASCADE)
    platform = models.CharField(max_length=24, choices=SOCIAL_PLATFORM_CHOICES)
    label = models.CharField(max_length=80, blank=True, help_text='Optional display name.')
    url = models.URLField(max_length=500)
    order = models.PositiveIntegerField(default=0)
    is_visible = models.BooleanField(default=True)

    class Meta:
        ordering = ['order', 'id']

    @property
    def display_name(self):
        return self.label or self.get_platform_display()

    def __str__(self):
        return self.display_name


class FocusItem(models.Model):
    """Manually curated work priorities for Overview (no external sync yet)."""

    class Status(models.TextChoices):
        IN_PROGRESS = 'in_progress', 'In progress'
        PLANNED = 'planned', 'Planned'
        PAUSED = 'paused', 'Paused'

    site = models.ForeignKey(SiteConfig, related_name='focus_items', on_delete=models.CASCADE)
    title = models.CharField(max_length=140)
    description = models.CharField(max_length=260, blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.IN_PROGRESS)
    order = models.PositiveIntegerField(default=0)
    is_visible = models.BooleanField(default=True)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return self.title


class UpdateItem(models.Model):
    """Manually published updates; not inferred from GitHub commits."""

    site = models.ForeignKey(SiteConfig, related_name='updates', on_delete=models.CASCADE)
    title = models.CharField(max_length=160)
    summary = models.CharField(max_length=280, blank=True)
    published_at = models.DateTimeField(default=timezone.now)
    url = models.URLField(blank=True, help_text='Optional link to more information.')
    is_visible = models.BooleanField(default=True)

    class Meta:
        ordering = ['-published_at', '-id']

    def __str__(self):
        return self.title


class JobMatchUsage(models.Model):
    """Short-lived, pseudonymous per-hour rate limit records; no job text stored."""

    visitor_hash = models.CharField(max_length=64)
    hour_bucket = models.DateTimeField()
    count = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['visitor_hash', 'hour_bucket'], name='job_match_usage_per_hour')]
