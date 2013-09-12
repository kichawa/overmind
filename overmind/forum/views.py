from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from forum.models import Topic, Post


def topics_list(request):
    topics = Topic.objects.select_related().order_by('updated')
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
    ctx = {
        'topic': topic,
        'posts': page,
    }
    return render(request, 'forum/posts_list.html', ctx)


def topic_create(request):
    raise NotImplementedError


def post_create(request, topic_pk):
    topic = get_object_or_404(Topic, pk=topic_pk)
    raise NotImplementedError
