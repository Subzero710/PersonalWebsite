from django.db import models
from django.utils.text import slugify


class SiteConfig(models.Model):
    full_name = models.CharField(max_length=120)
    headline = models.CharField(max_length=200, blank=True)
    email = models.EmailField(blank=True)
    github_url = models.URLField(blank=True)
    cv_file = models.FileField(upload_to="cv/", blank=True, null=True)
    avatar = models.ImageField(upload_to="avatar/", blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.full_name


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=80, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)[:80]
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name


class Project(models.Model):
    title = models.CharField(max_length=140)
    slug = models.SlugField(max_length=180, unique=True, blank=True)

    summary = models.CharField(max_length=240, blank=True)
    description = models.TextField(blank=True)

    tags = models.ManyToManyField(Tag, blank=True, related_name="projects")

    repo_url = models.URLField(blank=True)
    demo_url = models.URLField(blank=True)

    is_featured = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "-created_at"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:180]
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.title

class Highlight(models.Model):
    site = models.ForeignKey("SiteConfig", related_name="highlights", on_delete=models.CASCADE)
    text = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self) -> str:
        return self.text


class KPI(models.Model):
    site = models.ForeignKey("SiteConfig", related_name="kpis", on_delete=models.CASCADE)
    value = models.CharField(max_length=32)
    label = models.CharField(max_length=32)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self) -> str:
        return f"{self.value} — {self.label}"
