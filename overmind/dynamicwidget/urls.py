from django.conf.urls import patterns, url


urlpatterns = patterns('dynamicwidget.views',
    url(r'^widgets/$',
        'widgets',
        name="widgets"),
)
