import re

from django import template


register = template.Library()


@register.simple_tag
def mark_pattern(text, pattern, fmt=r'<span class="marked-pattern">\1</span>'):
    if pattern:
        rx = r"({})".format(re.escape(pattern))
        text = re.sub(rx, fmt, text, flags=re.IGNORECASE)
    return text
