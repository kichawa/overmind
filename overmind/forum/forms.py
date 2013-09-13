from django import forms
from django.db import transaction

from forum.models import Topic, Post, Tag



class TopicForm(forms.Form):
    subject = forms.CharField(
            required=True, min_length=3,
            max_length=Topic._meta.get_field('subject').max_length)
    content = forms.CharField(required=True, min_length=3,
                              widget=forms.Textarea())
    tags = forms.ModelMultipleChoiceField(queryset=Tag.objects.all())

    def __init__(self, data, instance=None):
        self.instance = instance
        super(TopicForm, self).__init__(data)

    def clean_subject(self):
        return self.cleaned_data.get('subject', '').strip()

    def clean_content(self):
        return self.cleaned_data.get('content', '').strip()

    def clean_tags(self):
        tags = self.cleaned_data.get('tags', ())
        if len(tags) < 2:
            raise forms.ValidationError('Select at least two tags')
        return tags

    @transaction.atomic
    def save(self):
        topic = self.instance
        topic.subject = self.cleaned_data['subject']
        topic.save()
        for tag in self.cleaned_data['tags']:
            topic.tags.add(tag)
        Post.objects.create(author=topic.author, topic=topic,
                            content=self.cleaned_data['content'])
        return topic


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('content', )
