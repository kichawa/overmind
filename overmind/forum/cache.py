from django.conf import settings
from django.shortcuts import get_object_or_404
from django.views.decorators.http import condition

from cachedb import Cache
from .models import Topic


cache = Cache(settings.CACHEDB_ADDRESS)


def expire_group(name):
    if not getattr(settings, 'HTTP_CACHE', False):
        return
    cache.delete_group(name)


def expire_groups(names):
    if not getattr(settings, 'HTTP_CACHE', False):
        return
    for name in names:
        cache.delete_group(name)


def latest_topics_update(request):
    if not getattr(settings, 'HTTP_CACHE', True):
        return None
    if request.GET.get('page', '1') != '1':
        return None
    topics = Topic.objects.select_related().order_by('-updated')
    tag_labels = request.GET.getlist('tag')
    if tag_labels:
        topics = topics.filter(tags__label__in=tag_labels)
    try:
        return topics[0].updated
    except IndexError:
        return None


topics_list = condition(last_modified_func=latest_topics_update)


def latest_topic_update(request, topic_pk):
    if not getattr(settings, 'HTTP_CACHE', True):
        return None
    topic = get_object_or_404(Topic, pk=topic_pk)
    return topic.updated


posts_list = condition(last_modified_func=latest_topic_update)
