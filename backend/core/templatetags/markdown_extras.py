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
