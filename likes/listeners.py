from utils.listeners import invalidate_object_cache
from utils.redis_helpers import RedisHelper


def incr_likes_count(sender, instance, created, **kwargs):
    if not created:
        return

    from tweets.models import Tweet
    from django.db.models import F

    model_class = instance.content_type.model_class()
    if model_class != Tweet:
        # TODO HOMEWORK 给 Comment 使用类似的方法进行 likes_count 的统计
        return

    # tweet = instance.content_object
    # 不可以使用 tweet.likes_count += 1; tweet.save() 的方式
    # 因此这个操作不是原子操作，必须使用 F函数 语句才是原子操作

    # F函数用法：
    # SQL Query: UPDATE likes_count = likes_count + 1 FROM tweets_table WHERE id=<instance.object_id>
    # 方法1：
    Tweet.objects.filter(id=instance.object_id)\
        .update(likes_count=F('likes_count') + 1)
    RedisHelper.incr_count(instance.content_object,'likes_count')

    # 方法2：
    # tweet = instance.content_object
    # tweet.likes_count = F('likes_count') + 1
    # tweet.save()


def decr_likes_count(sender, instance, **kwargs):
    from tweets.models import Tweet
    from django.db.models import F

    model_class = instance.content_type.model_class()
    if model_class != Tweet:
        # TODO HOMEWORK 给 Comment 使用类似的方法进行 likes_count 的统计
        return

    # tweet = instance.content_object
    # 不可以使用 tweet.likes_count -= 1; tweet.save() 的方式
    # 因此这个操作不是原子操作，必须使用 F函数 语句才是原子操作

    # F函数用法：
    # SQL Query: UPDATE likes_count = likes_count - 1 FROM tweets_table WHERE id=<instance.object_id>
    # 方法1：
    Tweet.objects.filter(id=instance.object_id)\
        .update(likes_count=F('likes_count') - 1)
    RedisHelper.decr_count(instance.content_object,'likes_count')

    # 方法2：
    # tweet = instance.content_object
    # tweet.likes_count = F('likes_count') - 1
    # tweet.save()
