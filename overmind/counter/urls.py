from django.conf.urls import patterns, url


urlpatterns = patterns('counter.views',
    url(r'^/$',
        'get_counter',
        name="get"),
)
