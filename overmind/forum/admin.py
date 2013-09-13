from django.contrib import admin

from forum import models


class PostAdmin(admin.TabularInline):
    model = models.Post


class TopicAdmin(admin.ModelAdmin):
    inlines = (PostAdmin, )


class UserProfileAdmin(admin.StackedInline):
    model = models.UserProfile


class UserAdmin(admin.ModelAdmin):
    inlines = (UserProfileAdmin, )



admin.site.register(models.Topic, TopicAdmin)
admin.site.register(models.User, UserAdmin)
admin.site.register(models.Tag)
