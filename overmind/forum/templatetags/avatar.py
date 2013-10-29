import hashlib
import urllib.parse

from django import template
from django.utils.safestring import mark_safe


register = template.Library()


@register.simple_tag
def avatar(email, width=32, height=None, **extra_params):
    if not height:
        height = width
    params = extra_params.copy()
    params.update({
        'gravatar': 'hashed',
        'size': '{}x{}'.format(width, height),
    })
    query = urllib.parse.urlencode(params)
    enc_email = str(hashlib.md5(email.lower().encode('utf8')).hexdigest())
    return  'http://robohash.org/{}.png?{}'.format(enc_email, query)


@register.simple_tag
def avatar_tag(email, width=32, height=None, **tag_attributes):
    if height is None:
        height = width
    url = avatar(email, width, height)
    attributes = [
        'width="{}px"'.format(width),
        'height="{}px"'.format(height),
    ]
    for name, value in tag_attributes.items():
        attributes.append('{}="{}"'.format(name, value))
    return mark_safe('<img src="{}" {}>'.format(url, ' '.join(attributes)))
