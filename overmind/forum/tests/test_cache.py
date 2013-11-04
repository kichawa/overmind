from django.test import TestCase

from forum import cache


class ListDict(dict):
    def getlist(self, name, default=()):
        if name in self:
            return self[name]
        return default


class GroupBuilderTest(TestCase):
    names = (
        'a:b',
        'a:{url:page}',
        'a:{get:tag}',
        'a:{url:page}:{get:tag}',
    )

    def setUp(self):
        self.builder = cache.create_names_builder(self.names)

    def test_empty(self):
        result = self.builder(ListDict(), {})
        expected = [
            'a:b',
            'a:',
            'a:',
            'a::',
        ]
        self.assertEqual(result, expected)

    def test_with_single_value(self):
        result = self.builder(ListDict(tag=['t1']), {'page': '3'})
        expected = [
            'a:b',
            'a:3',
            'a:t1',
            'a:3:t1',
        ]
        self.assertEqual(result, expected)

    def test_with_multiple_values(self):
        result = self.builder(ListDict(tag=['t1', 't2']), {'page': '3'})
        expected = [
            'a:b',
            'a:3',
            'a:t1,t2',
            'a:3:t1,t2',
        ]
        self.assertEqual(result, expected)

    def test_with_default_value(self):
        name = 'a:{url:page:1}:{get:tag}:{url:filter}'
        builder = cache.create_name_builder(name)

        result = builder(ListDict(), {})
        self.assertEqual(result, 'a:1::')
