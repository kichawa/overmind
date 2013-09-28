import re

from django import template


register = template.Library()


@register.simple_tag
def mark_pattern(post_content, pattern, css_class="marked-pattern"):
    replace = r'<span class="{0}">\g<0></span>'.format(css_class)
    output = re.sub(r'(?i){0}'.format(pattern), replace, post_content)
    return output
