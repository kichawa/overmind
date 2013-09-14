import datetime
import json

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.serializers.json import DjangoJSONEncoder
from django.core.urlresolvers import reverse
from django.conf import settings
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.timezone import utc

from forum.models import Topic, Post, Tag
from forum.forms import TopicForm, PostForm

TOPICS_PER_PAGE = getattr(settings, 'FORUM_TOPICS_PER_PAGE', 50)
POSTS_PER_PAGE = getattr(settings, 'FORUM_POSTS_PER_PAGE', 100)


def mark_topic_read(request, topic, last_post):
    # iso format is not precise enough, so we need to drop that precision too
    last_post_created = last_post.created.replace(microsecond=0)
    if not request.forum_profile:
        return
    if last_post_created < request.forum_profile.last_seen_all:
        return
    topic_last_seen = request.forum_profile.seen_topics.get(str(topic.id))
    if not topic_last_seen or topic_last_seen < last_post_created:
        request.forum_profile.seen_topics[str(topic.id)] = last_post_created
        request.forum_profile.save()


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

    # manage "new" topics
    if request.forum_profile:
        last_post = page.object_list[len(page.object_list) - 1]
        mark_topic_read(request, topic, last_post)

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
def api_user_profile(request):
    resp = {
        'last_seen_all': request.forum_profile.last_seen_all,
        'seen_topics': request.forum_profile.seen_topics,
    }
    return HttpResponse(json.dumps(resp, cls=DjangoJSONEncoder),
                        content_type='application/json')


@login_required
def mark_all_topics_read(request):
    now = datetime.datetime.now().replace(tzinfo=utc)
    request.forum_profile.last_seen_all = now
    request.forum_profile.seen_topics = {}
    request.forum_profile.save()
    return redirect(request.META.get('HTTP_REFERER', reverse('forum:topics-list')))
