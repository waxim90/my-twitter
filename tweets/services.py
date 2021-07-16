from tweets.models import TweetPhoto, Tweet
from twitter.cache import USER_TWEETS_PATTERN
from utils.redis_helpers import RedisHelper


class TweetService(object):

    @classmethod
    def create_photos_from_files(cls, tweet, files):
        photos = []
        for index, file in enumerate(files):
            photo = TweetPhoto(
                tweet=tweet,
                user=tweet.user,
                file=file,
                order=index,
            )
            photos.append(photo)
        TweetPhoto.objects.bulk_create(photos)

    @classmethod
    def get_cached_tweets(cls, user_id):
        # queryset 是懒惰加载，只有当iterate时才会去访问数据库获取内容
        queryset = Tweet.objects.filter(user_id=user_id).order_by('-created_at')
        key = USER_TWEETS_PATTERN.format(user_id=user_id)
        return RedisHelper.load_objects(key, queryset)

    @classmethod
    def push_tweet_to_cache(cls, tweet):
        # queryset 是懒惰加载，只有当iterate时才会去访问数据库获取内容
        queryset = Tweet.objects.filter(user_id=tweet.user_id).order_by('-created_at')
        key = USER_TWEETS_PATTERN.format(user_id=tweet.user_id)
        RedisHelper.push_object(key, tweet, queryset)
