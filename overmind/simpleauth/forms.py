from django import forms
from django.contrib.auth import get_user_model


class RegistrationForm(forms.Form):
    email = forms.EmailField()
    username = forms.RegexField(min_length=3, max_length=30,
                                regex=r'^[\w.@+-]+$')
    password = forms.CharField(min_length=6, max_length=128,
                               widget=forms.PasswordInput)
    password_repeat = forms.CharField(min_length=6, max_length=128,
                                      widget=forms.PasswordInput)
    antybot = forms.CharField(
            help_text="What's the name of Arch Linux package manager?")

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        User = get_user_model()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Email already registered")
        return email

    def clean_username(self):
        username = self.cleaned_data['username'].lower()
        User = get_user_model()
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("User name already registered")
        return username

    def clean_antybot(self):
        antybot = self.cleaned_data['antybot']
        if antybot != 'pacman':
            raise forms.ValidationError("You're not a true Arch Linux user!")
        return antybot

    def clean_password_repeat(self):
        repeat = self.cleaned_data['password_repeat']
        if self.cleaned_data['password'] != repeat:
            raise forms.ValidationError('Password does not match')
        return repeat

    def save(self):
        User = get_user_model()
        user = User(username=self.cleaned_data['username'],
                    email=self.cleaned_data['email'])
        user.set_password(self.cleaned_data['password'])
        user.save()
        return user
