import hashlib
import urllib.parse

from django.test import TestCase

from core.templatetags import avatar


class Gravatar(TestCase):
    def test_gravatar_url(self):
        email = 'bob@example.com'
        result = avatar.gravatar(email=email, width=40, height=50)
        url = urllib.parse.urlparse(result)
        hashed_email = str(hashlib.md5(email.encode('utf8')).hexdigest())
        self.assertEqual(url.path, '/{}.png'.format(hashed_email))
        query = urllib.parse.parse_qs(url.query)
        self.assertDictEqual(query, {
            'gravatar': ['hashed'],
            'size': ['40x50'],
        })


class GravatarTag(TestCase):
    def test_gravatar_tag(self):
        extra = {'class': 'avatar'}
        url = avatar.gravatar('bob@example.com', 40, 60)
        result = avatar.gravatar_tag('bob@example.com', 40, 60, **extra)
        expected = '<img src="{}" width="40px" height="60px" class="avatar">'.format(url)
        self.assertMultiLineEqual(result, expected)
