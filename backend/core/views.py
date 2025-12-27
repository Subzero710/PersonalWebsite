from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, render
from .models import Project, SiteConfig, Tag


def home(request):
    config = SiteConfig.objects.order_by("-updated_at").first()
    featured = Project.objects.filter(is_featured=True)[:6]
    return render(request, "core/home.html", {"config": config, "featured": featured})


def projects_list(request):
    config = SiteConfig.objects.order_by("-updated_at").first()
    projects = Project.objects.all()
    tags = Tag.objects.all().order_by("name")
    return render(request, "core/projects_list.html", {"config": config, "projects": projects, "tags": tags})

def project_detail(request, slug: str):
    config = SiteConfig.objects.order_by("-updated_at").first()
    project = get_object_or_404(Project, slug=slug)
    return render(request, "core/project_detail.html", {"config": config, "project": project})


def cv_download(request):
    config = SiteConfig.objects.order_by("-updated_at").first()
    if not config or not config.cv_file:
        raise Http404("CV not set")
    return FileResponse(config.cv_file.open("rb"), as_attachment=True, filename="CV.pdf")
