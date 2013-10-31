import urllib.parse

from django.conf import settings
from django.contrib import auth
from django.contrib.auth.views import login as django_login
from django.core.urlresolvers import reverse
from django.db import transaction
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from simpleauth.forms import RegistrationForm


def login(request):
    if request.method == 'GET' and not 'next' in request.GET:
        curr_url = urllib.parse.quote(request.META.get('HTTP_REFERER'))
        url = "{}?next={}".format(reverse('simpleauth:login'), curr_url)
        return redirect(url)
    return django_login(request)

@require_http_methods(["GET", "POST"])
@transaction.atomic
def register(request):
    form = RegistrationForm()
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            user = auth.authenticate(username=form.cleaned_data['username'],
                                     password=form.cleaned_data['password'])
            auth.login(request, user)
            dest = request.GET.get('next', settings.LOGIN_REDIRECT_URL)
            return redirect(dest)
    return render(request, "simpleauth/register.html", {'form': form})


def logout(request):
    if request.user.is_authenticated():
        auth.logout(request)
    dest = request.GET.get('next', request.META.get('HTTP_REFERER'))
    return redirect(dest)
