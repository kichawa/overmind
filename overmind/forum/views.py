import datetime
import json

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.serializers.json import DjangoJSONEncoder
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect

from forum.models import Topic, Post
from forum.forms import TopicForm, PostForm


def topics_list(request):
    topics = Topic.objects.select_related().prefetch_related('tags')\
            .order_by('-updated')
    paginator = Paginator(topics, 50)
    try:
        page = paginator.page(request.GET.get('page', 1))
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)
    ctx = {
        'topics': page,
    }
    return render(request, 'forum/topics_list.html', ctx)


def posts_list(request, topic_pk):
    topic = get_object_or_404(Topic, pk=topic_pk)
    posts = Post.objects.filter(topic=topic)\
            .select_related('author').order_by('created')
    paginator = Paginator(posts, 50)
    try:
        page = paginator.page(request.GET.get('page', 1))
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)

    # manage "new" topics
    last_post = page.object_list[len(page.object_list) - 1]
    if last_post.created > request.forum_profile.last_seen_all:
        topic_last_seen = request.forum_profile.seen_topics.get(topic.id)
        if not topic_last_seen or topic_last_seen < last_post.created:
            request.forum_profile.seen_topics[topic.id] = datetime.datetime.now()
            request.forum_profile.save()

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
        post = Post(topic=topic, author=request.forum_profile.user)
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save()
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
    request.forum_profile.last_seen_all = datetime.datetime.now()
    request.forum_profile.seen_topics = {}
    request.forum_profile.save()
    return redirect(request.META.get('HTTP_REFERER', reverse('forum:topics-list')))
