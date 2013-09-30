import markdown

from django import template
from django.utils.safestring import mark_safe


register = template.Library()


def markup_markdown(text):
    extensions = (
        'nl2br',
        'codehilite(guess_lang=False)',
        'tables',

    )
    return markdown.markdown(text, extensions=extensions,
                             output_format='html5', safe_mode='escape')


@register.filter
def markup(text, fmt='markdown'):
    text = text.strip()
    if fmt == 'markdown':
        html = markup_markdown(text)
    else:
        raise NotImplementedError('Makrup "{}" is not supported'.format(fmt))
    return mark_safe(html)
