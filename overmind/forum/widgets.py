from django.template import RequestContext
from django.template.loader import render_to_string

from forum.forms import PostForm
from forum.models import Topic, Post
from counter import backend
from dynamicwidget.decorators import widget_handler


@widget_handler(r"^topic-view-count:(?P<tid>\d+)$")
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


@widget_handler(r"^topic-is-new:(?P<tid>\d+)$")
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


@widget_handler(r"^login-logout$")
def login_logout(request, widgets):
    ctx = RequestContext(request)
    html = render_to_string('forum/widgets/login_logout.html', ctx)
    return {"login-logout": {"html": html}}


@widget_handler(r"post-is-new:(?P<pid>\d+)$")
def post_is_new(request, widgets):
    profile = request.forum_profile
    if not profile:
        return {w['wid']: {'html': ''} for w in widgets}

    query = Post.objects.filter(id__in=[w['params']['pid'] for w in widgets])
    posts = {}
    topics = {}
    newest = {}
    for pid, created, tid in query.values_list('id', 'created', 'topic_id'):
        created = created.replace(microsecond=0)
        posts[pid] = (tid, created)

        # find out, when the topic was last seen
        if tid not in topics:
            topic_last_seen = profile.seen_topics.get(str(tid), profile.last_seen_all)
            topic_last_seen = topic_last_seen.replace(microsecond=0)
            topics[tid] = topic_last_seen

        # find the newest post creation date for every related topic
        dt = newest.get(tid)
        if not dt:
            newest[tid] = created
        elif created > dt:
            newest[tid] = created

    res = {}
    for widget in widgets:
        post_id = int(widget['params']['pid'])
        tid, created = posts[post_id]
        is_new = created > topics[tid]
        if is_new:
            res[widget['wid']] = {'html': 'new'}
        else:
            res[widget['wid']] = {'html': ''}

    # make sure, we have all topics marked as "seen" with appropriate, fresh
    # date from the newest post we ask for
    for tid, newest_post_dt in newest.items():
        if newest_post_dt > topics[tid]:
            request.forum_profile.seen_topics[str(tid)] = newest_post_dt
            request.forum_profile.save()

    return res


@widget_handler(r"^topic-comment-form:(?P<tid>\d+)$")
def topic_comment_form(request, widgets):
    if not request.forum_profile:
        return {w['wid']: {'html': ''} for w in widgets}

    form = PostForm()
    res = {}
    ctx = RequestContext(request, {'form': form})
    for widget in widgets:
        ctx['topic_id'] = widget['params']['tid']
        html = render_to_string('forum/widgets/topic_comment_form.html', ctx)
        res[widget['wid']] = {'html': html}
    return res
