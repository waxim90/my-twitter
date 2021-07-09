from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_delete

from accounts.services import UserService
from friendships.listeners import invalidate_following_cache


class Friendship(models.Model):
    from_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='following_friendship_set'
    )
    to_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='follower_friendship_set'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        index_together = (
            # 获取我关注的所有人，按照关注时间排序
            ('from_user', 'created_at'),
            # 获得关注我的所有人，按照关注时间排序
            ('to_user', 'created_at'),
        )
        unique_together = (('from_user', 'to_user'),)
        ordering = ('-created_at',)

    def __str__(self):
        return f'{self.from_user} followed {self.to_user}'

    @property
    def cached_from_user(self):
        return UserService.get_user_through_cache(self.from_user_id)

    @property
    def cached_to_user(self):
        return UserService.get_user_through_cache(self.to_user_id)


# hook up with listeners to invalidate cache
pre_delete.connect(invalidate_following_cache, sender=Friendship)
post_save.connect(invalidate_following_cache, sender=Friendship)
