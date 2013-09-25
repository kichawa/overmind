import datetime

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.urlresolvers import reverse
from django.conf import settings
from django.db import transaction
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.timezone import utc
from django.views.decorators.http import condition

from forum.models import Topic, Post, Tag
from forum.forms import TopicForm, PostForm
from counter import backend


TOPICS_PER_PAGE = getattr(settings, 'FORUM_TOPICS_PER_PAGE', 50)
POSTS_PER_PAGE = getattr(settings, 'FORUM_POSTS_PER_PAGE', 100)



def latest_topics_update_condition(request):
    if 'q' in request.GET:
        return None
    topics = Topic.objects.select_related().order_by('-updated')
    tag_labels = request.GET.getlist('tag')
    if tag_labels:
        topics = topics.filter(tags__label__in=tag_labels)
    try:
        return topics[0].updated
    except IndexError:
        return None


@condition(last_modified_func=latest_topics_update_condition)
def topics_list(request):
    topics = Topic.objects.select_related().prefetch_related('tags')\
            .order_by('-updated')

    if 'tag' in request.GET:
        labels = request.GET.getlist('tag')
        topics = topics.filter(tags__label__in=labels).distinct()

    if 'q' in request.GET:
        q = request.GET['q']
        # this is spartaaa!
        full_text_filter = Q(subject__icontains=q) | Q(posts__content__icontains=q)
        topics = topics.filter(full_text_filter).distinct()


    paginator = Paginator(topics, TOPICS_PER_PAGE)
    try:
        page = paginator.page(request.GET.get('page', 1))
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)

    tags = []
    for tag in Tag.objects.all():
        tags.append({
            'label': tag.label,
            'checked': tag.label in request.GET.getlist('tag'),
        })

    ctx = {
        'topics': page,
        'tags': tags,
    }
    return render(request, 'forum/topics_list.html', ctx)


def latest_topic_update_condition(request, topic_pk):
    topic = get_object_or_404(Topic, pk=topic_pk)
    result = topic.updated

    # not sure if this is the best place for this, probably not and this
    # should be done with the javascript
    #
    # manage the "new" topics (this should be never affected by the cache)
    if request.forum_profile:
        if topic.updated <= request.forum_profile.last_seen_all:
            return result
        topic_last_seen = request.forum_profile.seen_topics.get(str(topic.id))
        if topic_last_seen \
                and topic_last_seen <= topic.updated.replace(microsecond=0):
            return result

        # at this point, the only thing we can do is to apply pagination and
        # update the profile data
        posts = Post.objects.filter(topic=topic)\
                .select_related('author').order_by('created')
        paginator = Paginator(posts, POSTS_PER_PAGE)
        try:
            page = paginator.page(request.GET.get('page', 1))
        except PageNotAnInteger:
            page = paginator.page(1)
        except EmptyPage:
            page = paginator.page(paginator.num_pages)
        last_post = page.object_list[len(page.object_list) - 1]
        # iso format is not precise enough, so we need to drop that precision too
        last_post_created = last_post.created.replace(microsecond=0)
        if not request.forum_profile:
            return result
        if last_post_created < request.forum_profile.last_seen_all:
            return result
        if not topic_last_seen or topic_last_seen < last_post_created:
            request.forum_profile.seen_topics[str(topic.id)] = last_post_created
            request.forum_profile.save()

    return result


@condition(last_modified_func=latest_topic_update_condition)
def posts_list(request, topic_pk):
    topic = get_object_or_404(Topic, pk=topic_pk)
    posts = Post.objects.filter(topic=topic)\
            .select_related('author').order_by('created')
    paginator = Paginator(posts, POSTS_PER_PAGE)
    try:
        page = paginator.page(request.GET.get('page', 1))
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)

    # this is not always called (condition cache decorator), but that's good
    # thing. It means that the same user is not bumping the counter all the
    # time
    counter = backend.default()
    counter.increment('topic:view:{}'.format(topic.pk))

    ctx = {
        'topic': topic,
        'posts': page,
        'post_form': PostForm(),
    }
    return render(request, 'forum/posts_list.html', ctx)


@login_required
def topic_create(request):
    if request.method == 'POST':
        topic = Topic(author=request.forum_profile.user)
        form = TopicForm(request.POST, instance=topic)
        if form.is_valid():
            topic = form.save()
            return redirect(topic.get_absolute_url())
    else:
        form = TopicForm()
    ctx = {'form': form}
    return render(request, 'forum/topic_create.html', ctx)


@login_required
def post_create(request, topic_pk):
    topic = get_object_or_404(Topic, pk=topic_pk)
    if request.method == 'POST':
        with transaction.autocommit():
            post = Post(topic=topic, author=request.forum_profile.user)
            form = PostForm(request.POST, instance=post)
            if form.is_valid():
                post = form.save()
                topic.response_count = topic.posts.count() - 1
                topic.updated = post.created
                topic.save()
                return redirect(post.get_absolute_url())
    else:
        form = PostForm()
    ctx = {'topic': topic, 'form': form}
    return render(request, 'forum/post_create.html', ctx)


@login_required
def mark_all_topics_read(request):
    now = datetime.datetime.now().replace(tzinfo=utc)
    request.forum_profile.last_seen_all = now
    request.forum_profile.seen_topics = {}
    request.forum_profile.save()
    return redirect(request.META.get('HTTP_REFERER', reverse('forum:topics-list')))
