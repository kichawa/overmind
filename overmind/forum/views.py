import datetime

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.core.urlresolvers import reverse
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.timezone import utc
from django.views.decorators.cache import never_cache

from counter import backend

from . import cache
from .models import Topic, Post, Tag, LastSeen
from .forms import TopicForm, PostForm, SearchForm


def posts_search(request):
    form = SearchForm()

    if request.GET.get('pattern', None):
        form = SearchForm(request.GET)
    else:
        form = SearchForm()

    if form.is_valid():
        posts = Post.objects.select_related().order_by('-created')
        tag_labels = request.GET.getlist('tag')
        if tag_labels:
            posts = posts.filter(topic__tags__label__in=tag_labels).distinct()
        pattern = form.cleaned_data.get('pattern')
        posts = posts.filter(content__icontains=pattern)
    else:
        posts = Post.objects.none()

    paginator = Paginator(posts,
                          getattr(settings, 'FORUM_SEARCH_RESULT_PER_PAGE', 25))
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
        'form': form,
        'posts': page,
        'tags': tags,
        'pattern': form.is_valid() and form.cleaned_data.get('pattern', None),
    }
    return render(request, 'forum/posts_search.html', ctx)



@cache.topics_list
def topics_list(request):
    topics = Topic.objects.select_related().prefetch_related('tags')\
            .order_by('-updated')

    tag_labels = request.GET.getlist('tag')
    if tag_labels:
        topics = topics.filter(tags__label__in=tag_labels).distinct()

    paginator = Paginator(topics, settings.FORUM_TOPICS_PER_PAGE)
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
        'POSTS_PER_PAGE': settings.FORUM_POSTS_PER_PAGE,
    }
    return render(request, 'forum/topics_list.html', ctx)


@cache.posts_list
def posts_list(request, topic_pk):
    topic = get_object_or_404(Topic, pk=topic_pk)
    posts = Post.objects.filter(topic=topic)\
            .select_related('author').order_by('created')
    paginator = Paginator(posts, settings.FORUM_POSTS_PER_PAGE)
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
    }
    return render(request, 'forum/posts_list.html', ctx)


@never_cache
def posts_list_last_page(request, topic_pk):
    topic = get_object_or_404(Topic, pk=topic_pk)
    return redirect(topic.get_absolute_url(last_page=True))


@login_required
def topic_create(request):
    if request.method == 'POST':
        topic = Topic(author=request.user)
        form = TopicForm(request.POST, instance=topic)
        form = TopicForm(request.POST, instance=topic)
        if form.is_valid():
            ip = request.META.get('REMOTE_ADDR')
            topic = form.save(ip)
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
            post = Post(topic=topic, author=request.user)
            form = PostForm(request.POST, instance=post)
            if form.is_valid():
                post = form.save(commit=False)
                post.ip = request.META.get('REMOTE_ADDR')
                post.save()
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
    last_seen = LastSeen.obtain_for(request.user)
    last_seen.last_seen_all = now
    last_seen.seen_topics = {}
    last_seen.save()
    return redirect(request.META.get('HTTP_REFERER', reverse('forum:topics-list')))


def user_details(request, user_pk):
    user = get_object_or_404(get_user_model(), pk=user_pk)
    ctx = {'user': user}
    return render(request, 'forum/user_details.html', ctx)
