from django.conf.urls import patterns, url


urlpatterns = patterns('forum.views',
    url(r'^$',
        'topics_list',
        name="topics-list"),
    url(r'^topic/create/$',
        'topic_create',
        name="topic-create"),
    url(r'^topic/mark-all-read/$',
        'mark_all_topics_read',
        name="mark-all-topics-read"),
    url(r'^topic/(?P<topic_pk>\d+)/(?:([^/]+)/)?comment/$',
        'post_create',
        name="post-create"),
    url(r'^topic/(?P<topic_pk>\d+)/(?:([^/]+)/)?toggle-delete/$',
        'topic_toggle_delete',
        name="topic-toggle-delete"),
    url(r'^topic/(?P<topic_pk>\d+)/(?:([^/]+)/)?report-as-spam/$',
        'topic_report_as_spam',
        name="topic-report-as-spam"),
    url(r'^topic/(?P<topic_pk>\d+)/(?:([^/]+)/)?last-page/$',
        'posts_list_last_page',
        name="posts-list-last-page"),
    url(r'^topic/(?:([^/]+)/)?(?P<topic_pk>\d+)/$',
        'posts_list',
        name="posts-list"),
    url(r'^topic/(?P<topic_pk>\d+)/post/(?P<post_pk>\d+)/toggle-delete/$',
        'post_toggle_delete',
        name="post-toggle-delete"),
    url(r'^topic/(?P<topic_pk>\d+)/post/(?P<post_pk>\d+)/details/$',
        'post_details',
        name="post-details"),
    url(r'^topic/(?P<topic_pk>\d+)/post/(?P<post_pk>\d+)/edit/$',
        'post_edit',
        name="post-edit"),
    url(r'^topic/(?P<topic_pk>\d+)/post/(?P<post_pk>\d+)/report-as-spam/$',
        'post_report_as_spam',
        name="post-report-as-spam"),
    url(r'search/$',
        'posts_search',
        name="posts-search"),
    url(r'user/(?P<user_pk>\d+)/$',
        'user_details',
        name="user-details"),
)
