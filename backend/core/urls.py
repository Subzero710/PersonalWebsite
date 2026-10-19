from django.urls import path
from . import views, job_matching_views

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("tech-stack/", views.tech_stack, name="tech_stack"),
    path("projects/", views.projects_list, name="projects_list"),
    path("projects/<slug:slug>/", views.project_detail, name="project_detail"),
    path("cv/", views.cv_download, name="cv_download"),
    path("tools/job-matching/generate/", job_matching_views.job_matching_generate, name="job_matching_generate"),
]