from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, render
from .models import SiteConfig, Project, Highlight, KPI, Skill, Tag


def _site_context():
    config = SiteConfig.objects.order_by('-updated_at').first()
    nav_projects = list(Project.objects.filter(is_featured=True).only('title', 'slug', 'icon_key')
                        .order_by('order', '-created_at')[:3])

    # Explicit skills always win. On a migrated older site, show real project
    # technologies instead of inventing skills or leaving an empty section.
    skills = list(Skill.objects.filter(site=config, is_visible=True)) if config else []
    skills_from_tags = False
    if not skills:
        from django.db.models import Count
        skills = list(Tag.objects.filter(projects__isnull=False)
                      .annotate(project_count=Count('projects', distinct=True))
                      .order_by('-project_count', 'name').distinct()[:7])
        skills_from_tags = bool(skills)
    return {'config': config, 'nav_projects': nav_projects,
            'skills': skills, 'skills_from_tags': skills_from_tags,
            'has_skills': bool(skills)}


def home(request):
    context = _site_context()
    config = context['config']
    context.update({
        'featured': Project.objects.filter(is_featured=True).prefetch_related('tags').order_by('order', '-created_at')[:3],
        'highlights': Highlight.objects.filter(site=config) if config else Highlight.objects.none(),
        'kpis': KPI.objects.filter(site=config) if config else KPI.objects.none(),
    })
    return render(request, 'core/home.html', context)


def projects_list(request):
    context = _site_context()
    context.update({
        'projects': Project.objects.prefetch_related('tags').all(),
        'tags': Tag.objects.filter(projects__isnull=False).distinct().order_by('name'),
    })
    return render(request, 'core/projects_list.html', context)


def project_detail(request, slug: str):
    context = _site_context()
    context['project'] = get_object_or_404(Project.objects.prefetch_related('tags'), slug=slug)
    return render(request, 'core/project_detail.html', context)


def cv_download(request):
    config = SiteConfig.objects.order_by('-updated_at').first()
    if not config or not config.cv_file:
        raise Http404('CV not set')
    return FileResponse(config.cv_file.open('rb'), as_attachment=True, filename='MyResume.pdf')
