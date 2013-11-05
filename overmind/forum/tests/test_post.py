from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.test import Client, TransactionTestCase
from django.test.utils import override_settings

from forum.models import Topic, Post


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
        self.assertEqual(topic.response_count, 3)
        url = reverse('forum:post-create', args=(topic.pk, ))
        data = {'content': 'comment by bob'}
        resp = self.client.post(url, data)
        post = topic.posts.order_by('-created')[0]
        topic = Topic.objects.get(pk=2)
        self.assertEqual(post.content, data['content'])
        self.assertEqual(post.author.username, 'bobross')
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(topic.response_count, 4)
        self.assertEqual(topic.response_count, topic.posts.count() - 1)
        self.assertEqual(topic.updated, post.created)


class PostDetailsPageTest(TransactionTestCase):
    fixtures = ['forum/tests/small_size_forum.yaml']

    @override_settings(FORUM_POSTS_PER_PAGE=2)
    def test_redirects(self):
        test_data = (
            (2, 2, 'topic/2/2013-09-02-second-topic/#post-2'),
            (2, 3, 'topic/2/2013-09-02-second-topic/#post-3'),
            (2, 4, 'topic/2/2013-09-02-second-topic/?page=2#post-4'),
            (2, 5, 'topic/2/2013-09-02-second-topic/?page=2#post-5'),
        )
        for topic_pk, post_pk, url_suffix in test_data:
            resp = self.client.get(
                    reverse('forum:post-details', args=(topic_pk, post_pk,)))
            self.assertEqual(resp.status_code, 302)
            self.assertTrue(resp.url.endswith(url_suffix),
                            "{} does not end with {}".format(resp.url, url_suffix))

    def test_redirect_post_deleted(self):
        post = Post.objects.get(pk=2)
        post.is_deleted = True
        post.save()
        resp = self.client.get(
                reverse('forum:post-details', args=(post.topic_id, post.pk, )))
        self.assertEqual(resp.status_code, 404)

    def test_redirect_topic_deleted(self):
        post = Post.objects.get(pk=2)
        post.topic.is_deleted = True
        post.topic.save()
        resp = self.client.get(
                reverse('forum:post-details', args=(post.topic_id, post.pk, )))
        self.assertEqual(resp.status_code, 404)

