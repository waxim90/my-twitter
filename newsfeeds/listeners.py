def push_newsfeed_to_cache(sender, instance, created, **kwargs):
    # 只有新建时才push， update时并不push
    if not created:
        return

    from newsfeeds.services import NewsFeedService
    NewsFeedService.push_newsfeed_to_cache(instance)