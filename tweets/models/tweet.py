from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import pre_delete, post_save

from likes.models import Like
from tweets.listeners import push_tweet_to_cache
from utils.memcached_helpers import MemcachedHelper
from utils.time_helpers import utc_now
from utils.listeners import invalidate_object_cache


class Tweet(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        help_text='who posts this tweet',
    )
    content = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    # 新增的 field 一定要设置 null=True，否则 default = 0 会遍历整个表单去设置
    # 导致 Migration 过程非常慢，从而把整张表单锁死，从而正常用户无法创建新的 tweets
    likes_count = models.IntegerField(default=0, null=True)
    comments_count = models.IntegerField(default=0, null=True)

    class Meta:
        index_together = (('user', 'created_at'),)
        ordering = ('user', '-created_at')

    def __str__(self):
        # 这里是你执行 print(tweet instance) 的时候会显示的内容
        return f'{self.created_at} {self.user}: {self.content}'

    @property
    def hours_to_now(self):
        # datetime.now 不带时区信息，需要增加上 utc 的时区信息
        return (utc_now() - self.created_at).seconds // 3600

    # @property
    # def comments(self):
    #     return self.comment_set.all()
    #     # return Comment.objects.filter(tweet=self)

    @property
    def like_set(self):
        return Like.objects.filter(
            content_type=ContentType.objects.get_for_model(Tweet),
            object_id=self.id,
        ).order_by('-created_at')

    @property
    def cached_user(self):
        return MemcachedHelper.get_object_through_cache(User, self.user_id)


# hook up with listeners to invalidate memcached cache
pre_delete.connect(invalidate_object_cache, sender=Tweet)
post_save.connect(invalidate_object_cache, sender=Tweet)

# hook up with listeners to push to redis cache
post_save.connect(push_tweet_to_cache, sender=Tweet)
