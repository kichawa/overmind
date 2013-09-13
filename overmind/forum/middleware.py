import datetime

from django.utils.functional import SimpleLazyObject

from forum.models import UserProfile, User


class UserProfileMiddleware(object):
    def process_request(self, request):
        def forum_profile():
            if not hasattr(request, '_cached_forum_profile'):
                if request.user.is_anonymous():
                    request._cached_forum_profile = None
                else:
                    # we can do this, because both models have the same id
                    user = User(pk=request.user.id)
                    profile, _ = UserProfile.objects.get_or_create(user=user,
                            defaults={'last_seen_all': datetime.datetime(2000, 1, 1)})
                    request._cached_forum_profile = profile
            return request._cached_forum_profile

        request.forum_profile = SimpleLazyObject(forum_profile)
