import collections
import json
import re

from django.http import HttpResponse

from forum.models import Topic
from counter import backend


_widgets = []


def register_widget(rx):
    def decorator(view):
        _widgets.append((re.compile(rx), view))
        return view

    return decorator


def widget(request):
    wids = request.GET.getlist('wid')
    handlers = collections.defaultdict(list)
    for wid in wids:
        for rx, view in _widgets:
            res = rx.match(wid)
            if res:
                handlers[view].append({'wid': wid, 'params': res.groupdict()})
                break
        else:
            handlers[not_found_handler].append({'wid': wid})

    result = {}
    for handler, args in handlers.items():
        result.update(handler(request, args))
    content = json.dumps(result)
    return HttpResponse(content, content_type='application/json')


def not_found_handler(request, widgets):
    res = {}
    for widget in widgets:
        res[widget['wid']] = {
            'error': 'No handler for widget "{}"'.format(widget['wid']),
        }
    return res


@register_widget("^topic-view-count:(?P<tid>\d+)$")
def topic_view_count(request, widgets):
    key_tmpl = "topic:view:{}"
    counter = backend.default()
    keys = [key_tmpl.format(w['params']['tid']) for w in widgets]
    counters = counter.get(keys)
    res = {}
    for widget in widgets:
        value = counters.get(key_tmpl.format(widget['params']['tid']), 0)
        res[widget['wid']] = {
            'html': '<span class="counter">{}</span>'.format(value)
        }
    return res


@register_widget("^topic-is-new:(?P<tid>\d+)$")
def topic_is_new(request, widgets):
    if request.user.is_anonymous():
        return {w['wid']: {'html': ''} for w in widgets}

    topics = {}
    query = Topic.objects.filter(id__in=[w['params']['tid'] for w in widgets])
    for tid, updated in query.values_list('id', 'updated'):
        topics[tid] = updated
    res = {}
    seen_topics = request.forum_profile.seen_topics
    for widget in widgets:
        topic_id = int(widget['params']['tid'])
        last_seen = seen_topics.get(str(topic_id),
                                    request.forum_profile.last_seen_all)
        updated = topics.get(topic_id)
        if updated < last_seen:
            html = ''
        else:
            html = '*'
        res[widget['wid']] = {'html': html}
    return res


@register_widget("login-logout")
def login_logout(request, widgets):
    if request.user.is_authenticated():
        html = '<a href="/auth/logout/">Logout</a>'
    else:
        html = '<a href="/auth/">Login</a>'
    return {"login-logout": {"html": html}}
