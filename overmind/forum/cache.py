import functools
import re

from django.conf import settings
from django.shortcuts import get_object_or_404
from django.views.decorators.http import condition

from cachedb import Cache
from .models import Topic


# cache only those response objects that response_code is in following set
CACHABLE_RESPONSE_CODE = {200, 301, 404}


if getattr(settings, 'HTTP_CACHE', False):
    cache = Cache(settings.CACHEDB_ADDRESS)
else:
    cache = None



def expire_group(name):
    if not getattr(settings, 'HTTP_CACHE', False):
        return
    cache.delete_group(name)


def expire_groups(names):
    if not getattr(settings, 'HTTP_CACHE', False):
        return
    for name in names:
        cache.delete_group(name)


_group_param_rx = re.compile(r'{[^}]+}')


def create_name_builder(name_repr):
    """Return a name buidler function for given string

    Group builder is a function, that for given string and set of parameters
    (url and GET parameters) can generate string containing choosed data. For
    example, for view parameter id=5 and GET parameter page=2:

    "key_{url:id}_{get:page}" => "key_5_2"

    """
    live_parts = _group_param_rx.findall(name_repr)
    dynamic_chunks = []
    for part in live_parts:
        chunks = part[1:-1].split(':', 3)
        if len(chunks) == 2:
            default = ''
            tp, name = chunks
        else:
            tp, name, default = chunks
        if tp not in ['url', 'get']:
            raise TypeError('unknown cache parameter type: {}'.format(tp))
        dynamic_chunks.append((tp, name, default))
    dynamic_chunks.append(None)
    static_chunks = _group_param_rx.split(name_repr)

    def builder(params, kwargs):
        chunks = []
        for static, dynamic in zip(static_chunks, dynamic_chunks):
            chunks.append(static)
            if dynamic is None:
                continue
            if dynamic[0] == 'url':
                chunks.append(kwargs.get(dynamic[1], dynamic[2]))
            else:
                items = params.getlist(dynamic[1], ())
                if items:
                    value = ','.join(items)
                else:
                    value = dynamic[2]
                chunks.append(value)
        return ''.join(chunks)

    return builder


def create_names_builder(groups):
    "For given set of group names, return list of builder functions"
    builders = []
    for group in groups:
        builders.append(create_name_builder(group))
    builders = tuple(builders)

    def builder(params, kwargs):
        return [fn(params, kwargs) for fn in builders]

    return builder


def cache_view(key, groups=(), last_modified_func=None):
    """Cache view

    This can use two layers cache:

    1) cache response object
    2) provide "Last-Modified" header variable

    Every view cache can be assigned to any number of dynamic groups for ease
    of multiple key expiration.

    If `last_modified_func` is provided, it's result is cached with the same
    groups as the response object.
    """
    # XXX  this does not properly cache gzip header
    nil = object()
    gbuilder = create_names_builder(groups)
    kbuilder = create_name_builder(key)

    def decorator(view):
        if not getattr(settings, 'HTTP_CACHE', False):
            return view

        @functools.wraps(view)
        def wrapper(request, *args, **kwargs):
            view_fn = view
            key = kbuilder(request.GET, kwargs)

            if last_modified_func:
                # if last modified function is provided, wrap it with group
                # cache and reuse the result
                def cached_last_modified_func(*args, **kwargs):
                    key_last_modified = key + ':last_modified'
                    result = cache.getset(key_last_modified, nil)
                    if result is nil:
                        result = last_modified_func(*args, **kwargs)
                        cache.set(key_last_modified, result,
                                  groups=gbuilder(request.GET, kwargs))
                    return result
                view_fn = condition(last_modified_func=cached_last_modified_func)(view_fn)

            response = cache.getset(key, nil)
            if response is nil:
                response = view_fn(request, *args, **kwargs)
                if response.status_code in CACHABLE_RESPONSE_CODE:
                    cache.set(key, response,
                              groups=gbuilder(request.GET, kwargs))
            return response

        return wrapper
    return decorator


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


topics_list = cache_view('topics:{get:page:1}:{get:tag}', groups=('topic:all',),
                         last_modified_func=latest_topics_update)


def latest_topic_update(request, topic_pk):
    if not getattr(settings, 'HTTP_CACHE', True):
        return None
    topic = get_object_or_404(Topic, pk=topic_pk)
    return topic.updated


posts_list = cache_view('posts_list:{url:topic_pk}:{get:page:1}',
                        groups=('topic:all', 'topic:{url:topic_pk}'),
                        last_modified_func=latest_topic_update)
