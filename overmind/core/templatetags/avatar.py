import hashlib
import urllib.parse

from django import template
from django.utils.safestring import mark_safe


register = template.Library()


@register.simple_tag
def gravatar(email, width=32, height=None):
    if not height:
        height = width
    enc_email = str(hashlib.md5(email.lower().encode('utf8')).hexdigest())
    default = "http://robohash.org/bgset_bg3/{}.png?size={}x{}".format(
            enc_email, width, height)
    params = urllib.parse.urlencode({
        'd': default,
        's': str(width)
    })

    return "http://www.gravatar.com/avatar/{}?{}".format(enc_email, params)


@register.simple_tag
def gravatar_tag(email, width=32, height=None, **tag_attributes):
    url = gravatar(email, width, height)
    attributes = [
        'width="{}px"'.format(width),
        'heigth="{}px"'.format(height),
    ]
    for name, value in tag_attributes.items():
        attributes.append('{}="{}"'.format(name, value))
    return mark_safe('<img src="{}" {}>'.format(url, ' '.join(attributes)))
