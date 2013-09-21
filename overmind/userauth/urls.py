from django.conf.urls import patterns, url


urlpatterns = patterns('userauth.views',
    url(r'^begin/$',
        'begin',
        name="openid-begin"),
    url(r'^complete/$',
        'complete',
        name="openid-complete"),
)
