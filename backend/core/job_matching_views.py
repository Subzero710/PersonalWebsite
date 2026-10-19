"""Public, CSRF-protected job-match report endpoint. No submitted text is persisted."""

import hashlib
import hmac
import ipaddress
from datetime import timedelta

from django import forms
from django.conf import settings
from django.db import transaction
from django.db.models import F
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.http import require_POST

from .job_matching import MatchingFailed, MatchingUnavailable, build_evidence, call_model
from .job_matching_pdf import build_pdf, filename_for
from .models import Highlight, JobMatchUsage, Project, SiteConfig, Skill
from .job_matching_setup import setup_issues


class JobMatchForm(forms.Form):
    job_title = forms.CharField(max_length=140, min_length=2, strip=True)
    company = forms.CharField(max_length=120, required=False, strip=True)
    job_description = forms.CharField(min_length=40, max_length=12000, strip=True)


def _visitor_hash(request):
    # X-Real-IP is set/overwritten by the site's Nginx reverse proxy; the web
    # container is not publicly bound to a host port (docker-compose expose).
    candidate = request.META.get('HTTP_X_REAL_IP') or request.META.get('REMOTE_ADDR', '')
    try:
        visitor_ip = str(ipaddress.ip_address(candidate))
    except ValueError:
        visitor_ip = str(request.META.get('REMOTE_ADDR', 'unknown'))[:64]
    return hmac.new(settings.SECRET_KEY.encode('utf-8'),
                    visitor_ip.encode('utf-8'), hashlib.sha256).hexdigest()


def _claim_quota(request, limit=3):
    now = timezone.now()
    hour_bucket = now.replace(minute=0, second=0, microsecond=0)
    visitor = _visitor_hash(request)
    with transaction.atomic():
        row, _ = JobMatchUsage.objects.get_or_create(
            visitor_hash=visitor, hour_bucket=hour_bucket, defaults={'count': 0})
        claimed = JobMatchUsage.objects.filter(pk=row.pk, count__lt=limit).update(count=F('count') + 1)
    # Do not indefinitely retain even pseudonymous fingerprints.
    JobMatchUsage.objects.filter(created_at__lt=now - timedelta(hours=48)).delete()
    return bool(claimed)


@require_POST
@csrf_protect
@never_cache
@sensitive_post_parameters('job_description', 'job_title', 'company')
def job_matching_generate(request):
    if request.META.get('CONTENT_LENGTH', '').isdigit() and int(request.META['CONTENT_LENGTH']) > 60000:
        return JsonResponse({'error': 'The job description is too long (maximum 12,000 characters).'}, status=413)
    form = JobMatchForm(request.POST)
    if not form.is_valid():
        return JsonResponse({'error': 'Enter a job title and a job description (40–12,000 characters).'}, status=400)

    config = SiteConfig.objects.order_by('-updated_at').first()
    api_key = getattr(settings, 'JOB_MATCH_OPENAI_API_KEY', '')
    model = getattr(settings, 'JOB_MATCH_OPENAI_MODEL', 'gpt-4.1-mini')
    issues = setup_issues(config, api_key)
    if issues:
        return JsonResponse({
            'error': 'Job Matching setup incomplete: ' + ' '.join(issue['message'] for issue in issues),
            'missing': [issue['code'] for issue in issues],
        }, status=503)

    try:
        filename = filename_for(config.first_name, config.last_name, form.cleaned_data['job_title'])
    except ValueError:
        return JsonResponse({'error': 'The job title or configured name must contain Latin letters or numbers.'}, status=400)

    if not _claim_quota(request):
        return JsonResponse({'error': 'Hourly generation limit reached. Please try again later.'}, status=429)

    values = form.cleaned_data
    try:
        projects = list(Project.objects.all().prefetch_related('tags').order_by('order', '-created_at')[:24])
        skills = list(Skill.objects.filter(site=config, is_visible=True).order_by('order', 'id')[:40])
        highlights = list(Highlight.objects.filter(site=config).order_by('order', 'id')[:12])
        sources = build_evidence(config, projects, skills, highlights, request)
        report = call_model(
            values['job_title'], values['company'], values['job_description'], sources,
            api_key=api_key, model=model)
        pdf = build_pdf(
            title=values['job_title'], company=values['company'],
            first_name=config.first_name, last_name=config.last_name,
            report=report, public_url=request.build_absolute_uri('/'))
    except MatchingUnavailable as exc:
        return JsonResponse({'error': str(exc)}, status=503)
    except MatchingFailed as exc:
        return JsonResponse({'error': str(exc)}, status=502)

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    response['Cache-Control'] = 'no-store, private, max-age=0'
    response['X-Content-Type-Options'] = 'nosniff'
    return response
