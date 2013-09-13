from django import forms
from django.db import transaction

from forum.models import Topic, Post



class TopicForm(forms.Form):
    subject = forms.CharField(
            required=True, min_length=3,
            max_length=Topic._meta.get_field('subject').max_length)
    content = forms.CharField(required=True, min_length=3,
                              widget=forms.Textarea())

    def clean_subject(self):
        return self.cleaned_data.get('subject', '').strip()

    def clean_content(self):
        return self.cleaned_data.get('content', '').strip()

    @transaction.atomic
    def save(self):
        import pdb; pdb.set_trace()
        topic = Topic.objects.create(subject=self.cleaned_data['subject'])
        Post.objects.create(author=topic.user, topic=topic,
                            content=self.cleaned_data['content'])
        return topic


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('content', )
