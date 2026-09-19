"""
Renders blog post bodies as Markdown instead of Django's plain
`linebreaks` filter — needed for headers, tables, and bold/list content
to actually render as HTML rather than showing up as literal `####`/`|`
characters on the page.

mark_safe is used deliberately: post.body is only ever written by trusted
admin users (via /admin/ or the seed_*_posts management commands), never
by public/user submissions, so there's no XSS surface being opened here.
If that assumption ever changes (e.g. a public comment/submission field
gets added later), this filter must NOT be reused for that content without
adding sanitization first.
"""
import markdown as markdown_lib
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(name="markdownify")
def markdownify(text):
    if not text:
        return ""
    html = markdown_lib.markdown(text, extensions=["extra", "sane_lists"])
    return mark_safe(html)
