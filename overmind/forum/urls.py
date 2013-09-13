from django.conf.urls import patterns, url


urlpatterns = patterns('forum.views',
    url(r'^$',
        'topics_list',
        name="topics-list"),
    url(r'^topic/create/$',
        'topic_create',
        name="topic-create"),
    url(r'^topic/(?P<topic_pk>\d+)/(?:([^/]+)/)?comment/$',
        'post_create',
        name="post-create"),
    url(r'^topic/(?P<topic_pk>\d+)/(?:([^/]+)/)?$',
        'posts_list',
        name="posts-list"),
    url(r'^api/userprofile/$',
        'api_user_profile',
        name="api-user-profile"),
)
