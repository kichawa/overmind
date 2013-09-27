from django import template
from django.http import HttpRequest
import re

register = template.Library()


@register.simple_tag
def mark_pattern(post_content, pattern, css_class="marked-pattern"):
    replace = r'<span class="{0}">\g<0></span>'.format(css_class)
    output = re.sub(r'(?i){0}'.format(pattern), replace, post_content)
    return output
