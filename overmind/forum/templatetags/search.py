from django import template


register = template.Library()


@register.simple_tag
def mark_pattern(text, pattern, fmt='<span class="marked-pattern">{}</span>'):
    if pattern:
        subs = fmt.format(pattern)
        text = text.replace(pattern, subs)
    return text
