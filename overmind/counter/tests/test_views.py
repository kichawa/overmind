import json
import mock

from django.test import Client, TestCase
from django.core.urlresolvers import reverse

from counter.tests.backend import Memory



class CounterViewTest(TestCase):
    @mock.patch('counter.backend.default')
    def test_get(self, default_backend):
        backend = default_backend.return_value = Memory()
        backend.cache.set_many({'foo': 5, 'bar': 'baz'})
        cli = Client()
        url = reverse('counter:get')

        resp = cli.get(url, {'key': ['foo', 'bar', 'doesnotexist']})
        result = json.loads(resp.content.decode('utf8'))
        self.assertDictEqual(result, {'foo': 5, 'bar': 'baz'})
