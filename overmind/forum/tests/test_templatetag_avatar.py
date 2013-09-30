import hashlib
import urllib.parse

from django.test import TestCase

from forum.templatetags import avatar


class Gravatar(TestCase):
    def test_avatar_url(self):
        email = 'bob@example.com'
        result = avatar.avatar(email=email, width=40, height=50)
        url = urllib.parse.urlparse(result)
        hashed_email = str(hashlib.md5(email.encode('utf8')).hexdigest())
        self.assertEqual(url.path, '/{}.png'.format(hashed_email))
        query = urllib.parse.parse_qs(url.query)
        self.assertEqual(query['gravatar'], ['hashed'])
        self.assertEqual(query['size'],  ['40x50'])


class GravatarTag(TestCase):
    def test_avatar_tag(self):
        extra = {'class': 'avatar'}
        url = avatar.avatar('bob@example.com', 40, 60)
        result = avatar.avatar_tag('bob@example.com', 40, 60, **extra)
        expected = '<img src="{}" width="40px" height="60px" class="avatar">'.format(url)
        self.assertMultiLineEqual(result, expected)
