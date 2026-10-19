"""In-memory, evidence-cited PDF report using ReportLab. No generated files are persisted."""

import re
import unicodedata
from datetime import datetime, timezone
from html import escape
from io import BytesIO
from urllib.parse import urlparse

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    HRFlowable, Paragraph, SimpleDocTemplate, Spacer,
)

INK = colors.HexColor('#172334')
MUTED = colors.HexColor('#536477')
GREEN = colors.HexColor('#3f862c')
LINE = colors.HexColor('#dce4eb')


def slug_part(value):
    ascii_text = unicodedata.normalize('NFKD', str(value or '')).encode('ascii', 'ignore').decode('ascii')
    return re.sub(r'_+', '_', re.sub(r'[^a-z0-9]+', '_', ascii_text.lower())).strip('_')[:60]


def filename_for(first_name, last_name, title):
    parts = [slug_part(last_name), slug_part(first_name), slug_part(title)]
    if not all(parts):
        raise ValueError('First name, last name and job title are required for the PDF filename.')
    return '_'.join(parts) + '.pdf'


def _p(text):
    return escape(str(text or ''), quote=True).replace('\n', ' ')


def _link(url, label, style):
    parsed = urlparse(str(url))
    if parsed.scheme not in ('http', 'https') or not parsed.netloc:
        return Paragraph(_p(label), style)
    return Paragraph(f'<link href="{_p(url)}" color="#2258aa">{_p(label)}</link>', style)


def build_pdf(*, title, company, first_name, last_name, report, public_url):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=20*mm, leftMargin=20*mm,
                            topMargin=22*mm, bottomMargin=20*mm, title=f'Job Matching - {title}',
                            author=f'{first_name} {last_name}')
    styles = getSampleStyleSheet()
    h1 = ParagraphStyle('MainTitleCustom', parent=styles['Heading1'], fontName='Helvetica-Bold',
                        fontSize=20, leading=25, spaceAfter=9, textColor=INK)
    h2 = ParagraphStyle('SectionCustom', parent=styles['Heading2'], fontName='Helvetica-Bold',
                        fontSize=12, leading=16, spaceBefore=15, spaceAfter=8, textColor=INK)
    small = ParagraphStyle('SmallCustom', parent=styles['Normal'], fontName='Helvetica',
                           fontSize=9, leading=13.5, textColor=INK, spaceAfter=5)
    muted = ParagraphStyle('MutedCustom', parent=small, textColor=MUTED, fontSize=8.5, leading=12.5)
    body = ParagraphStyle('BodyCustom', parent=small, leading=14, spaceAfter=7)
    source = ParagraphStyle('SourceCustom', parent=muted, leftIndent=12, leading=12, spaceAfter=4)
    tiny = ParagraphStyle('TinyCustom', parent=muted, fontSize=8, leading=11)
    tag = ParagraphStyle('TagCustom', parent=muted, fontName='Helvetica-Bold', fontSize=8, textColor=GREEN)
    status_colors = {'documented': GREEN, 'related': colors.HexColor('#937021'), 'not_documented': MUTED}
    labels = {'documented': 'Documented evidence', 'related': 'Related / listed', 'not_documented': 'Not documented'}
    categories = {'responsibility': 'RESPONSIBILITY', 'required': 'REQUIRED', 'preferred': 'PREFERRED',
                  'experience': 'EXPERIENCE', 'other': 'OTHER'}

    story = [Paragraph('JOB MATCHING  /  EVIDENCE REPORT', tag), Spacer(1, 3),
             Paragraph(_p(title), h1), Paragraph(_p(f'Candidate: {first_name} {last_name}'), small)]
    if company:
        story.append(Paragraph(_p(f'Role at: {company}'), muted))
    story.extend([Paragraph(f'Prepared {datetime.now(timezone.utc):%d %B %Y} · Based on published portfolio data', muted),
                  Spacer(1, 8), HRFlowable(width='100%', thickness=.8, color=LINE),
                  Paragraph('01 — Summary', h2)])

    requirements = report['requirements']
    n_documented = sum(r['status'] == 'documented' for r in requirements)
    n_related = sum(r['status'] == 'related' for r in requirements)
    n_no = sum(r['status'] == 'not_documented' for r in requirements)
    story.append(Paragraph(
        f'This document compares <b>{len(requirements)}</b> requirements with published portfolio evidence: '
        f'<b>{n_documented}</b> documented, <b>{n_related}</b> related or listed, and '
        f'<b>{n_no}</b> not documented. These categories describe available evidence, '
        f'not the candidate\'s overall competence or a hiring recommendation.', body))

    story.append(Paragraph('02 — Requirements &amp; evidence', h2))
    for index, req in enumerate(requirements, 1):
        badge = labels[req['status']]
        kind = categories[req['category']]
        heading = Paragraph(f'<b>{index:02d}. {_p(req["requirement"])}</b>', small)
        status_style = ParagraphStyle(f'status-{index}', parent=tiny, textColor=status_colors[req['status']])
        first = [heading, Paragraph(f'{kind}  ·  {badge}', status_style)]
        if req.get('job_excerpt'):
            first.append(Paragraph(f'From the job posting: “{_p(req["job_excerpt"])}”', source))
        # Quote chunks can be moved across pages naturally if a requirement is long.
        story.extend(first)
        if not req['evidence']:
            story.append(Paragraph('No sufficiently specific supporting source was found in the published materials.', source))
        else:
            for evidence in req['evidence']:
                story.append(Paragraph(f'“{_p(evidence["excerpt"])}”', source))
                if evidence['url']:
                    story.append(_link(evidence['url'], f'Source: {evidence["label"]}', source))
                else:
                    story.append(Paragraph(_p(f'Source: {evidence["label"]}'), source))
        story.append(Spacer(1, 7))

    if report['projects']:
        story.append(Paragraph('03 — Most relevant projects', h2))
        for index, project in enumerate(report['projects'], 1):
            story.append(Paragraph(f'<b>{index}. {_p(project["title"])}</b>', small))
            if project['summary']:
                story.append(Paragraph(_p(project['summary']), muted))
            if project['tags']:
                story.append(Paragraph('Technologies: ' + _p(', '.join(project['tags'][:12])), tiny))
            story.append(_link(project['url'], 'Open portfolio project', tiny))
            if project.get('repo_url'):
                story.append(_link(project['repo_url'], 'Source repository', tiny))
            if project.get('demo_url'):
                story.append(_link(project['demo_url'], 'Live demo', tiny))
            story.append(Spacer(1, 6))
    appendix_number = '04' if report['projects'] else '03'
    story.extend([Paragraph(f'{appendix_number} — Interpretation &amp; limitations', h2),
                  Paragraph('A missing reference means <b>not demonstrated by the published material</b>, '
                            'not that the candidate lacks the skill. Project tags and listed skills alone '
                            'do not prove a depth of expertise. Quotations above are verified against '
                            'the portfolio/CV text supplied to the analysis.', body),
                  Paragraph('The job description was supplied by a recruiter. This report is automatically '
                            'generated and should be verified in an interview. It is not a CV, '
                            'an employment claim, or a suitability score.', muted)])
    if public_url:
        story.append(_link(public_url, 'View original portfolio', small))

    def footer(canvas, pdfdoc):
        canvas.saveState()
        width, _height = A4
        canvas.setStrokeColor(LINE)
        canvas.line(20*mm, 16*mm, width-20*mm, 16*mm)
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(MUTED)
        canvas.drawString(20*mm, 11*mm, 'JOB MATCHING · Evidence-based portfolio analysis')
        canvas.drawRightString(width-20*mm, 11*mm, f'{pdfdoc.page}')
        canvas.restoreState()

    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    return buffer.getvalue()
