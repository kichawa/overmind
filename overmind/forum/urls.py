from django.conf.urls import patterns, url


urlpatterns = patterns('forum.views',
    url(r'^$',
        'topics_list',
        name="forum-topics-list"),
    url(r'^topic/(?P<topic_pk>\d+)/(?:([^/]+)/)?$',
        'posts_list',
        name="forum-posts-list"),
)
