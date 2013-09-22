from django.conf.urls import patterns, url

from counter import views


urlpatterns = patterns('counter.views',
    url(r'^/$',
        views.Main.as_view(),
        name="main"),
    url(r'^increment/$',
        views.Increment.as_view(),
        name="increment"),
    url(r'^decrement/$',
        views.Decrement.as_view(),
        name="decrement"),
)
