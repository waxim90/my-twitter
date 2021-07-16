def push_tweet_to_cache(sender, instance, created, **kwargs):
    # 只有新建时才push， update时并不push
    if not created:
        return

    from tweets.services import TweetService
    TweetService.push_tweet_to_cache(instance)