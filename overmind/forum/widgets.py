from forum.models import Topic
from counter import backend

from dynamicwidget.decorators import widget_handler


@widget_handler("^topic-view-count:(?P<tid>\d+)$")
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


@widget_handler("^topic-is-new:(?P<tid>\d+)$")
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
        if updated.replace(microsecond=0) <= last_seen:
            html = ''
        else:
            html = '*'
        res[widget['wid']] = {'html': html}
    return res


@widget_handler("login-logout")
def login_logout(request, widgets):
    if request.user.is_authenticated():
        html = '<a href="/auth/logout/">Logout</a>'
    else:
        html = '<a href="/auth/">Login</a>'
    return {"login-logout": {"html": html}}
