import json
import mock

from django.test import Client, TestCase
from django.core.urlresolvers import reverse

from counter.tests.backend import Memory



class MainViewTest(TestCase):
    @mock.patch('counter.backend.default')
    def test_increment(self, default_backend):
        backend = default_backend.return_value = Memory()
        backend.cache.set_many({'foo': 5})
        cli = Client()
        url = reverse('counter:increment')

        resp = cli.put(url, json.dumps(['foo', 'baz']))
        result = json.loads(resp.content.decode('utf8'))
        self.assertDictEqual(result, {'foo': 6, 'baz': 1})

        resp = cli.put(url, json.dumps(['foo']))
        result = json.loads(resp.content.decode('utf8'))
        self.assertDictEqual(result, {'foo': 7})
        self.assertDictEqual(backend.cache._mem, {'foo': 7, 'baz': 1})

    @mock.patch('counter.backend.default')
    def test_decrement(self, default_backend):
        backend = default_backend.return_value = Memory()
        backend.cache.set_many({'foo': 5})
        cli = Client()
        url = reverse('counter:decrement')

        resp = cli.put(url, json.dumps(['foo', 'baz']))
        result = json.loads(resp.content.decode('utf8'))
        self.assertDictEqual(result, {'foo': 4, 'baz': -1})

        resp = cli.put(url, json.dumps(['foo']))
        result = json.loads(resp.content.decode('utf8'))
        self.assertDictEqual(result, {'foo': 3})
        self.assertDictEqual(backend.cache._mem, {'foo': 3, 'baz': -1})

    @mock.patch('counter.backend.default')
    def test_get(self, default_backend):
        backend = default_backend.return_value = Memory()
        backend.cache.set_many({'foo': 5, 'bar': 'baz'})
        cli = Client()
        url = reverse('counter:main')

        resp = cli.get(url, {'key': ['foo', 'bar', 'doesnotexist']})
        result = json.loads(resp.content.decode('utf8'))
        self.assertDictEqual(result, {'foo': 5, 'bar': 'baz'})

    @mock.patch('counter.backend.default')
    def test_set(self, default_backend):
        backend = default_backend.return_value = Memory()
        backend.cache.set_many({'foo': 5, 'bar': 'baz'})
        cli = Client()
        url = reverse('counter:main')

        resp = cli.post(url, {'foo': 123, 'baz': 'x'})
        self.assertEqual(resp.status_code, 201)
        self.assertDictEqual(backend.cache._mem,
                             {'foo': '123', 'bar': 'baz', 'baz': 'x'})
