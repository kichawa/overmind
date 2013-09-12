from django.db import models
from django.contrib.auth import get_user_model


class ForumUser(get_user_model()):
    class Meta:
        proxy = True

    @property
    def avatar(self):
        return 'http://robohash.org/{}.png'.format(self.username)


class Topic(models.Model):
    subject = models.CharField(max_length=256)
    author = models.ForeignKey(ForumUser)


class Post(models.Model):
    topic = models.ForeignKey(Topic)
    author = models.ForeignKey(ForumUser)
    content = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
