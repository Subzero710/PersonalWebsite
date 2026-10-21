from django import template
from django.utils.safestring import mark_safe
import markdown as md
import bleach

register = template.Library()

_ALLOWED_TAGS = [
    "p", "br", "hr",
    "strong", "em", "code", "pre", "blockquote",
    "ul", "ol", "li",
    "h1", "h2", "h3", "h4",
    "a",
]
_ALLOWED_ATTRS = {
    "a": ["href", "title", "rel", "target"],
}
_ALLOWED_PROTOCOLS = ["http", "https", "mailto"]

@register.filter
def markdown_safe(value: str) -> str:
    if not value:
        return ""
    html = md.markdown(
        value,
        extensions=["fenced_code", "tables", "nl2br"],
        output_format="html5",
    )
    cleaned = bleach.clean(
        html,
        tags=_ALLOWED_TAGS,
        attributes=_ALLOWED_ATTRS,
        protocols=_ALLOWED_PROTOCOLS,
        strip=True,
    )
    cleaned = bleach.linkify(cleaned)
    return mark_safe(cleaned)


# Display the actual shipped technology logo when a Tag/Skill name matches an
# SVG asset. The name still comes from the database, never from a stub list.
from functools import lru_cache
import re
from django.contrib.staticfiles import finders
from django.templatetags.static import static
from django.utils.text import slugify

_TECH_ALIASES = {
    'html': 'html5', 'html-5': 'html5',
    'css': 'css3', 'css-3': 'css3',
    'spring-boot': 'spring', 'springboot': 'spring', 'spring-framework': 'spring',
    'postgres': 'postgresql', 'postgres-sql': 'postgresql', 'postgre-sql': 'postgresql',
    'sqlite3': 'sqlite', 'mysql8': 'mysql',
    'js': 'javascript', 'ts': 'typescript', 'node': 'nodejs', 'node-js': 'nodejs',
    'golang': 'go', 'go-lang': 'go', 'reactjs': 'react', 'react-js': 'react',
    'next-js': 'nextjs', 'next': 'nextjs',
    'amazon-web-services': 'aws', 'k8s': 'kubernetes',
    'vite': 'vitejs', 'vite-js': 'vitejs',
    'mongo-db': 'mongodb', 'mongo': 'mongodb',
    # Django slugify("C++") and slugify("C#") both produce "c".
    # Resolve technology names before slugification to avoid wrong branding.
    'c++': 'cplusplus', 'cpp': 'cplusplus', 'c-plus-plus': 'cplusplus',
    'c#': 'csharp', 'c-sharp': 'csharp',
    'scikit-learn': 'scikitlearn', 'scikit_learn': 'scikitlearn',
    'gitlab-ci-cd': 'gitlab', 'gitlab-ci': 'gitlab',
    'javafx': 'java',
}

@lru_cache(maxsize=128)
def _technology_icon_url(key: str) -> str:
    key = _TECH_ALIASES.get(key, key)
    if not re.fullmatch(r"[a-z0-9-]{1,40}", key):
        return ""
    asset = f"core/icons/skills/{key}.svg"
    return static(asset) if finders.find(asset) else ""

@register.filter
def skill_icon_src(item) -> str:
    """Prefer uploaded image, then icon_key, then an existing SVG by name."""
    if getattr(item, "icon_image", None):
        return item.icon_image.url
    name = getattr(item, "name", "").strip().casefold()
    # Prioritize the exact display name for C, C++ and C# even if a legacy
    # row contains slug="c". All other tags allow manually chosen icon_key.
    special_names = {"c": "c", "c++": "cplusplus", "c#": "csharp"}
    keys = ([special_names[name]] if name in special_names else [
        getattr(item, "icon_key", ""), name, slugify(name)
    ])
    for key in keys:
        result = _technology_icon_url(key)
        if result:
            return result
    return ""
