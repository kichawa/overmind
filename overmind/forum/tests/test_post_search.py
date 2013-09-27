from django.test import TransactionTestCase, Client, TestCase
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.template import Template, Context, TemplateSyntaxError

from forum.models import Post


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
        out = Template(
                "{% load search %}"
                "{% mark_pattern 'third response in second post. kichawa Kichawa KiChAwA' 'kichawa' %}"
                ).render(Context({
                    'pattern': 'kichawa', 
                    }))
        proper = 'third response in second post. <span class="marked-pattern">kichawa</span> <span class="marked-pattern">Kichawa</span> <span class="marked-pattern">KiChAwA</span>'
        self.assertEqual(out, proper)
