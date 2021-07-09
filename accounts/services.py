from django.conf import settings
from django.core.cache import caches
from accounts.models import UserProfile
from twitter.cache import USER_PROFILE_PATTERN

cache = caches['testing'] if settings.TESTING else caches['default']


class UserService:

    # 已经包装到 utils/memcached_helpers 下面了
    # @classmethod
    # def get_user_through_cache(cls, user_id):
    #     key = USER_PATTERN.format(user_id=user_id)
    #
    #     # read from cache first
    #     user = cache.get(key)
    #     # cache hit return
    #     if user is not None:
    #         return user
    #
    #     # cache miss, read from db
    #     try:
    #         user = User.objects.get(id=user_id)
    #         cache.set(key, user)
    #     except User.DoesNotExist:
    #         user = None
    #     return user
    #
    # @classmethod
    # def invalidate_user_cache(cls, user_id):
    #     key = USER_PATTERN.format(user_id=user_id)
    #     cache.delete(key)

    @classmethod
    def get_profile_through_cache(cls, user_id):
        key = USER_PROFILE_PATTERN.format(user_id=user_id)
        profile = cache.get(key)
        if profile is not None:
            return profile

        # cache miss, read from db
        profile, _ = UserProfile.objects.get_or_create(user_id=user_id)
        cache.set(key, profile)
        return profile

    @classmethod
    def invalidate_profile_cache(cls, user_id):
        key = USER_PROFILE_PATTERN.format(user_id=user_id)
        cache.delete(key)
