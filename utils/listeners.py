def invalidate_object_cache(sender, instance, **kwargs):
    from utils.memcached_helpers import MemcachedHelper
    MemcachedHelper.invalidate_object_cache(sender, instance.id)