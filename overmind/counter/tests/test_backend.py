from django.test import TestCase

from counter import backend
from counter.tests.backend import Memcache


class CacheBackendTest(TestCase):
    def setUp(self):
        self.memcache = Memcache()
        self.backend = backend.Cache(self.memcache)

    def test_increment(self):
        self.memcache.set_many({'b': 3})
        res = self.backend.increment('a', 'b')
        self.assertDictEqual(res, {'a': 1, 'b': 4})
        res = self.backend.increment('a', 'b', value=3)
        self.assertDictEqual(res, {'a': 4, 'b': 7})

    def test_decrement(self):
        self.memcache.set_many({'b': 3})
        res = self.backend.decrement('a', 'b')
        self.assertDictEqual(res, {'a': -1, 'b': 2})
        res = self.backend.decrement('a', 'b', value=2)
        self.assertDictEqual(res, {'a': -3, 'b': 0})

    def test_get(self):
        self.memcache.set_many({'b': 'bla'})
        res = self.backend.get('a', 'b')
        self.assertDictEqual(res, {'b': 'bla'})

    def test_set(self):
        self.memcache.set_many({'b': 'bla'})
        self.backend.set(a='foo', b='bar')
        self.assertDictEqual(self.memcache._mem, {'a': 'foo', 'b': 'bar'})
