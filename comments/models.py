from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db import models

from likes.models import Like
from tweets.models import Tweet
from utils.memcached_helpers import MemcachedHelper


class Comment(models.Model):
    """
    这个版本中，我们先实现一个比较简单的评论
    评论只评论在某个Tweet上，不能评论别人的评论
    """
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    tweet = models.ForeignKey(Tweet, on_delete=models.SET_NULL, null=True)
    content = models.TextField(max_length=140)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # 有在某个 tweet 下排序所有 comments 的需求
        index_together = (('tweet', 'created_at'),)

    def __str__(self):
        return '{created_at} - {user} says {content} at tweet {tweet_id}'.format(
            created_at=self.created_at,
            user=self.user,
            content=self.content,
            tweet_id=self.tweet_id,
        )

    @property
    def like_set(self):
        return Like.objects.filter(
            content_type=ContentType.objects.get_for_model(Comment),
            object_id=self.id,
        ).order_by('-created_at')

    @property
    def cached_user(self):
        return MemcachedHelper.get_object_through_cache(User, self.user_id)