from django.conf.urls import patterns, url


urlpatterns = patterns('',
    url(r'^login/$',
        'django.contrib.auth.views.login',
        name="login"),
    url(r'^logout/$',
        'simpleauth.views.logout',
        name="logout"),
    url(r'^register/$',
        'simpleauth.views.register',
        name="register"),
)
