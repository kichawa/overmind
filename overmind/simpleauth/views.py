from django.contrib import auth
from django.conf import settings
from django.db import transaction
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods

from simpleauth.forms import RegistrationForm


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
            return redirect(settings.LOGIN_REDIRECT_URL)
    return render(request, "simpleauth/register.html", {'form': form})


def logout(request):
    if request.user.is_authenticated():
        auth.logout(request)
    return redirect(settings.LOGIN_REDIRECT_URL)
