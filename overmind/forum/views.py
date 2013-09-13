from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib.auth.decorators import login_required

from forum.models import Topic, Post, ForumUser
from forum.forms import TopicForm, PostForm


def topics_list(request):
    topics = Topic.objects.select_related().order_by('-updated')
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
        'post_form': PostForm(),
    }
    return render(request, 'forum/posts_list.html', ctx)


@login_required
def topic_create(request):
    if request.method == 'POST':
        form = TopicForm(request.POST)
        if form.is_valid():
            forum_user = ForumUser.objects.get(id=request.user.id)
            topic = Topic(author=forum_user)
            topic = form.save(instance=topic)
            return redirect(topic.get_absolute_url())
    else:
        form = TopicForm()
    ctx = {'form': form}
    return render(request, 'forum/topic_create.html', ctx)


@login_required
def post_create(request, topic_pk):
    topic = get_object_or_404(Topic, pk=topic_pk)
    if request.method == 'POST':
        forum_user = ForumUser.objects.get(id=request.user.id)
        post = Post(topic=topic, author=forum_user)
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save()
            return redirect(post.get_absolute_url())
    else:
        form = PostForm()
    ctx = {'topic': topic, 'form': form}
    return render(request, 'forum/post_create.html', ctx)
