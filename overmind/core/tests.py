from urllib import parse

from django.test import TestCase

from core.templatetags import urlquery


class TestUrlqueryTemplatetag(TestCase):
    def test_query_add(self):
        test_data = (
            ('', {'a': 1}, 'a=1'),
            ('a=1', {'a': 2}, 'a=1&a=2'),
            ('a=1', {'b': 3}, 'a=1&b=3'),
            ('a=1', {'a': 4, 'b': 3}, 'a=1&a=4&b=3'),
        )
        for query, kwargs, expected in test_data:
            result = urlquery.urlquery_add(query, **kwargs)
            self.assertDictEqual(parse.parse_qs(result),
                                 parse.parse_qs(expected))

    def test_query_remove(self):
        test_data = (
            ('', (), {'a': 1}, ''),
            ('a=1', (), {'a': 2}, 'a=1'),
            ('a=1&b=3', (), {'a': 1}, 'b=3'),
            ('a=1&b=1&b=2', (), {'a': 1, 'b': 1}, 'b=2'),
            ('a=1&b=3', ('a', ), {}, 'b=3'),
            ('a=1&a=4&b=3', ('a', ), {}, 'b=3'),
            ('a=1&b=1&b=2&c=3', ('c'), {'a': 1, 'b': 1}, 'b=2'),
        )

        for query, args, kwargs, expected in test_data:
            result = urlquery.urlquery_remove(query, *args, **kwargs)
            self.assertDictEqual(parse.parse_qs(result),
                                 parse.parse_qs(expected))

    def test_query_set(self):
        test_data = (
            ('', {'a': 1}, 'a=1'),
            ('a=1&a=4', {'a': 2}, 'a=2'),
            ('a=1&b=3', {'b': 1}, 'a=1&b=1'),
            ('a=1&b=3', {'c': 1}, 'a=1&b=3&c=1'),
        )
        for query, kwargs, expected in test_data:
            result = urlquery.urlquery_set(query, **kwargs)
            self.assertDictEqual(parse.parse_qs(result),
                                 parse.parse_qs(expected))
