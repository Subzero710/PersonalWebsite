from django.db import models
from django.utils.text import slugify

# Icon values select visual assets, never project/skill content.
ICON_CHOICES = [
    ('', 'No icon'), ('cloud', 'Cloud'), ('code', 'Code'), ('globe', 'Web'),
    ('terminal', 'Terminal'), ('server', 'Server'), ('database', 'Database'),
    ('layers', 'Layers'), ('package', 'Package'), ('settings', 'Settings'),
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
    headline = models.CharField(max_length=200, blank=True)
    hero_title = models.CharField(max_length=180, blank=True)
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
            self.slug = slugify(self.name)[:80]
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
    icon_key = models.CharField(max_length=20, blank=True, choices=ICON_CHOICES)
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
