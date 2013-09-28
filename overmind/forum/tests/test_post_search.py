from django.core.urlresolvers import reverse
from django.test import TransactionTestCase, Client, TestCase

from forum.templatetags import search


class PostsSearchTest(TransactionTestCase):
    fixtures = ['forum/tests/small_size_forum.yaml']

    def setUp(self):
        self.client = Client()

    def test_post_create(self):
        url = reverse('forum:posts-search')
        data = {'pattern': 'kichawa'}
        resp = self.client.get(url, data)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context['posts'].paginator.count, 2)


class MarkPostTest(TestCase):
    def test_mark_post(self):
        test_data = (
            ('', '', ''),
            ('', 'foo', ''),
            ('foo baz bar', '', 'foo baz bar'),
            ('foo baz bar foo', 'baz', 'foo [baz] bar foo'),
            ('foofoofoo', 'foo', '[foo][foo][foo]'),
            ('foofoofoo', 'oo', 'f[oo]f[oo]f[oo]'),
        )

        for input_data, pattern, expected in test_data:
            result = search.mark_pattern(input_data, pattern, fmt='[{}]')
            self.assertMultiLineEqual(result, expected)
