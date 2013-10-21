from http.client import HTTPConnection
from urllib.parse import urlparse

from django.conf import settings
from django.shortcuts import get_object_or_404
from django.views.decorators.http import condition

from .models import Topic


def expire_group(name):
    return expire_groups((name, ))[0]


def expire_groups(names):
    try:
        return _expire_groups(names)
    except ConnectionRefusedError:
        return [None for _ in names]


def _expire_groups(names):
    results = []
    url = urlparse(settings.GROUPCACHE_URL)
    conn = HTTPConnection(url.netloc)
    for name in names:
        conn.request("DELETEGROUP", "{}/{}".format(url.path, name))
        resp = conn.getresponse()
        # just because we're sending one after another
        resp.read()
        if resp.status == 204:
            results.append(True)
            continue
        if resp.status == 404:
            results.append(False)
            continue
        # don't worry about errors
        results.append(None)
    conn.close()
    return results


def latest_topics_update(request):
    if not getattr(settings, 'HTTP_CACHE', True):
        return None
    if request.GET.get('q'):
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
