from django.db.models import Count
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, render
from .models import SiteConfig, Project, KPI, Tag, SocialLink, FocusItem, UpdateItem
from .job_matching_setup import setup_issues


_NON_TECH_TAG_NAMES = {
    'ai', 'cnn', 'networking', 'distributed', 'distributed systems',
    'cybersecurity', 'security research', 'ci/cd', 'gitlab ci/cd',
    'reinforcement learning', 'automated testing', 'web scraping',
    'git', 'github', 'gitlab',
}

_TECH_NAME_ALIASES = {'springboot': 'spring boot'}


def _technology_wall(config):
    """Restore project-linked Tags as the only Tech Stack data source."""
    # Restore the exact pre-patch Tag source: technologies attached to projects.
    technologies = Tag.objects.filter(projects__isnull=False).distinct()
    unique = {}
    for tag in technologies:
        name = tag.name.strip()
        folded = name.casefold()
        if not folded or folded in _NON_TECH_TAG_NAMES:
            continue
        key = _TECH_NAME_ALIASES.get(folded, folded)
        unique.setdefault(key, tag)
    return sorted(unique.values(), key=lambda tag: tag.name.casefold())


def _site_context():
    config = SiteConfig.objects.order_by('-updated_at').first()
    nav_projects = list(Project.objects.filter(is_featured=True).only('title', 'slug', 'icon_key')
                        .order_by('order', '-created_at')[:3])

    # All social links are contact destinations. Links contains the main
    # GitHub destination and the CV, configured separately in SiteConfig.
    contact_links = []
    resource_social_links = []
    seen_social_urls = set()
    if config:
        if config.email:
            contact_links.append({'label': 'Email',
                                  'url': f'mailto:{config.email}',
                                  'icon': 'mail', 'external': False})
        for social in SocialLink.objects.filter(
            site=config, is_visible=True
        ).order_by('order', 'id'):
            normalized = social.url.strip().rstrip('/').casefold()
            if not normalized or normalized in seen_social_urls:
                continue
            seen_social_urls.add(normalized)
            contact_links.append({
                'label': social.display_name,
                'url': social.url,
                'icon': social.platform,
                'external': True,
            })

    from django.conf import settings
    job_matching_issues = setup_issues(config, getattr(settings, 'JOB_MATCH_OPENAI_API_KEY', ''))
    job_matching_ready = not job_matching_issues

    return {'config': config, 'nav_projects': nav_projects,
            'job_matching_ready': job_matching_ready,
            'job_matching_issues': job_matching_issues,
            'contact_links': contact_links,
            'resource_social_links': resource_social_links}


def home(request):
    context = _site_context()
    config = context['config']
    context.update({
        'featured': Project.objects.filter(is_featured=True).prefetch_related('tags').order_by('order', '-created_at')[:3],
        'focus_items': FocusItem.objects.filter(site=config, is_visible=True)[:3] if config else [],
        'recent_updates': UpdateItem.objects.filter(site=config, is_visible=True)[:4] if config else [],
        'kpis': KPI.objects.filter(site=config).order_by('order', 'id') if config else [],
    })
    return render(request, 'core/home.html', context)


def about(request):
    context = _site_context()
    return render(request, 'core/about.html', context)


def tech_stack(request):
    context = _site_context()
    context['technologies'] = _technology_wall(context['config'])
    return render(request, 'core/tech_stack.html', context)


def projects_list(request):
    context = _site_context()
    context.update({
        'projects': Project.objects.prefetch_related('tags').all(),
        'tags': (Tag.objects.filter(projects__isnull=False)
                 .annotate(project_count=Count('projects', distinct=True))
                 .order_by('-project_count', 'name')),
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
