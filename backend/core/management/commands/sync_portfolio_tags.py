"""Conservative, repo-URL-matched portfolio tag audit. No data edits without --apply.

    python manage.py sync_portfolio_tags
    python manage.py sync_portfolio_tags --apply

Only projects linked to explicit GitHub repositories are considered. No projects,
descriptions, or existing tag rows are deleted or overwritten.
"""

from urllib.parse import urlparse

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.text import slugify

from core.models import Project, Tag


# Curated from source files, READMEs and manifests (October 2026).
# Each association represents a directly evidenced part of the project.
# Source/vendor repositories do not imply the author developed their upstream code.
PROJECT_TECHNOLOGIES = {
    "PersonalWebsite": (
        "Python", "Django", "PostgreSQL", "Docker", "Nginx", "Gunicorn",
        "TypeScript", "JavaScript", "HTML", "CSS", "esbuild",
    ),
    "IARISS-website": ("HTML", "CSS", "JavaScript", "Google Apps Script"),
    "kanbin": (
        "Java", "Spring", "JavaScript", "HTML", "CSS", "Maven",
        "Automated Testing", "GitLab CI/CD",
    ),
    "DeepLearning": (
        "Python", "NumPy", "pandas", "scikit-learn", "TensorFlow", "Keras",
        "Flask", "Java", "Spring Boot", "Docker",
    ),
    "Mosaic": (
        "Python", "Rust", "PostgreSQL", "Docker", "SQLAlchemy",
        "LightGBM", "scikit-learn", "WebSocket", "Parquet",
    ),
    "Hyperliquid_Archiver": (
        "Python", "Docker", "SQLite", "WebSocket", "S3", "LZ4",
    ),
    "LeChiffre": ("Rust", "Tokio"),
    "gpt_trace_extractor_for_cyberbenchmarking": (
        "Python", "Docker", "PostgreSQL", "FastAPI", "KVM/QEMU",
        "MCP", "Automated Testing", "pytest",
    ),
    "World-of-Tank-BI-analysis": ("Python", "Web Scraping", "pandas", "Beautiful Soup"),
    "textutils": ("Python", "Automated Testing", "pytest"),
    "IHM_project": ("Java", "JavaFX", "Maven"),
    "Flight": ("Java", "JavaFX", "Maven"),
    "TimeSeries": ("C++", "CMake"),
    "Zoo": ("C++", "CMake"),
    "PokemonGame": ("C++",),
    "Drawing-Robot-unity-": ("C#", "Unity"),
    "IQS": ("Python", "OpenCV", "NumPy"),
    "TD-IA-reinforcement-learning": ("Python", "Reinforcement Learning", "NumPy", "Gymnasium"),
    "Vaccine-Efficiency": ("Python", "NumPy", "Matplotlib"),
    "Connect4": ("Python",),
    "AlgoDistrib": ("Java", "Maven", "Distributed Systems"),
    "container-escape-nginx-proxy-demo": (
        "Python", "Docker", "Nginx", "FastAPI", "PostgreSQL", "Redis",
        "Grafana", "Prometheus", "JavaScript", "Vite", "HTML", "CSS",
    ),
    "arbitrary-code-execution-on-local-dev-POC": (
        "Python", "Docker", "Linux", "Git", "Security Research",
    ),
    # Intentionally omit CVE-2024-3094-demo (mostly authentic upstream XZ code)
    # and Tauric (upstream TradingAgents) to avoid attributing their tech as
    # original implementation without evidence of a user's own changes.
}

# Narrow replacements, only on the repository linked to its original tooling.
# The global Tag records themselves are never deleted.
LEGACY_ASSOCIATIONS = {
    "kanbin": ("JaCoCo",),
    "World-of-Tank-BI-analysis": ("Selenium",),
}

SPECIAL_SLUGS = {"c++": "cplusplus", "c#": "csharp"}


def github_repository(url):
    """Recognize only github.com/Subzero710/<exact repo>, not arbitrary URLs."""
    parsed = urlparse((url or "").strip())
    if parsed.scheme not in ("https", "http") or parsed.netloc.casefold() != "github.com":
        return None
    parts = [part for part in parsed.path.strip("/").split("/") if part]
    if len(parts) != 2 or parts[0].casefold() != "subzero710":
        return None
    name = parts[1].removesuffix(".git")
    return next((key for key in PROJECT_TECHNOLOGIES if key.casefold() == name.casefold()), None)


def existing_tag(name):
    matches = list(Tag.objects.filter(name__iexact=name)[:2])
    if len(matches) > 1:
        raise CommandError(f"Ambiguous existing tags for {name!r}; resolve manually")
    return matches[0] if matches else None


def tag_for_name(name):
    current = existing_tag(name)
    if current:
        return current, False
    slug = SPECIAL_SLUGS.get(name.casefold(), slugify(name))
    if not slug:
        raise CommandError(f"Empty slug for {name!r}")
    if Tag.objects.filter(slug=slug).exists():
        raise CommandError(f"Slug {slug!r} already used; manually resolve {name!r}")
    return Tag.objects.create(name=name, slug=slug), True


class Command(BaseCommand):
    help = "Review/append verified project tags without removing existing tags or project data"

    def add_arguments(self, parser):
        parser.add_argument("--apply", action="store_true", help="Commit additions and narrow legacy tag swaps")
        parser.add_argument("--repo", help="Only process this GitHub repository name")

    def handle(self, *args, **options):
        apply = options["apply"]
        only_repo = options.get("repo")
        if only_repo and only_repo.casefold() not in {name.casefold() for name in PROJECT_TECHNOLOGIES}:
            raise CommandError(f"Unknown --repo {only_repo!r}")
        total_created = total_linked = total_detached = matched = 0
        with transaction.atomic():
            for project in Project.objects.prefetch_related("tags").order_by("pk"):
                repo = github_repository(project.repo_url)
                if not repo or (only_repo and repo.casefold() != only_repo.casefold()):
                    continue
                matched += 1
                existing_names = {tag.name.casefold() for tag in project.tags.all()}
                additions = [name for name in PROJECT_TECHNOLOGIES[repo] if name.casefold() not in existing_names]
                legacy = [tag for tag in project.tags.all()
                          if tag.name.casefold() in {name.casefold() for name in LEGACY_ASSOCIATIONS.get(repo, ())}]
                self.stdout.write(f"{project.title} [{repo}]: +{', '.join(additions) or 'none'}"
                                  f" | detach: {', '.join(t.name for t in legacy) or 'none'}")
                if not apply:
                    continue
                for name in additions:
                    tag, created = tag_for_name(name)
                    project.tags.add(tag)
                    total_created += int(created)
                    total_linked += 1
                # Removes only the old project<->tag link, not the Tag row.
                for tag in legacy:
                    project.tags.remove(tag)
                    total_detached += 1
        self.stdout.write(f"Projects matched: {matched}. " + (
            f"Applied: created {total_created} tags; linked {total_linked}; detached {total_detached} legacy associations."
            if apply else "DRY RUN: database unchanged. Add --apply after reviewing the proposed associations."
        ))
