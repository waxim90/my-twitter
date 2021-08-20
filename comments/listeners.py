from utils.listeners import invalidate_object_cache
from utils.redis_helpers import RedisHelper


def incr_comments_count(sender, instance, created, **kwargs):
    if not created:
        return

    from tweets.models import Tweet
    from django.db.models import F

    # handle new comment
    # 不可以使用 tweet.comments_count += 1; tweet.save() 的方式
    # 因此这个操作不是原子操作，必须使用 F函数 语句才是原子操作

    # 方法1：
    Tweet.objects.filter(id=instance.tweet_id)\
        .update(comments_count=F('comments_count') + 1)
    RedisHelper.incr_count(instance.tweet,'comments_count')

    # 方法2：
    # tweet = instance.tweet
    # tweet.comments_count = F('comments_count') + 1
    # tweet.save()


def decr_comments_count(sender, instance, **kwargs):
    from tweets.models import Tweet
    from django.db.models import F

    # handle comment deletion
    Tweet.objects.filter(id=instance.tweet_id)\
        .update(comments_count=F('comments_count') - 1)
    RedisHelper.decr_count(instance.tweet,'comments_count')

    # 方法2：
    # tweet = instance.content_object
    # tweet.likes_count = F('likes_count') - 1
    # tweet.save()
