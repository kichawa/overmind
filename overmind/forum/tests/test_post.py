from django.test import TransactionTestCase, Client
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse

from forum.models import Topic


class PostCreationTest(TransactionTestCase):
    fixtures = ['forum/tests/small_size_forum.yaml']

    def setUp(self):
        u = get_user_model().objects.get(username='bobross')
        u.set_password('a')
        u.save()
        self.client = Client()
        self.assertTrue(self.client.login(username='bobross', password='a'))

    def test_post_create(self):
        topic = Topic.objects.get(pk=2)
        self.assertEqual(topic.response_count, 1)
        url = reverse('forum:post-create', args=(topic.pk, ))
        data = {'content': 'comment by bob'}
        resp = self.client.post(url, data)
        post = topic.posts.order_by('-created')[0]
        topic = Topic.objects.get(pk=2)
        self.assertEqual(post.content, data['content'])
        self.assertEqual(post.author.username, 'bobross')
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(topic.response_count, 2)
        self.assertEqual(topic.response_count, topic.posts.count() - 1)
        self.assertEqual(topic.updated, post.created)
