from django.db import models
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.utils.text import slugify


class ForumUser(get_user_model()):
    class Meta:
        proxy = True

    @property
    def avatar_url(self):
        return 'http://robohash.org/bgset_bg3/{}.png?size=80x80'.format(self.username)


class Topic(models.Model):
    subject = models.CharField(max_length=256)
    author = models.ForeignKey(ForumUser)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now_add=True)

    def get_absolute_url(self):
        slug = slugify('{}-{}'.format(self.created.date(), self.subject))
        return reverse('forum:posts-list', args=(self.pk, slug))

    def __str__(self):
        return self.subject


class Post(models.Model):
    topic = models.ForeignKey(Topic)
    author = models.ForeignKey(ForumUser)
    content = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content[:120]

    def get_absolute_url(self):
        return self.topic.get_absolute_url()
