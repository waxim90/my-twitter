from django.conf import settings

from django_hbase.models import HBaseModel
from utils.redis_client import RedisClient
from utils.redis_serializers import DjangoModelSerializer, HBaseModelSerializer


class RedisHelper:

    @classmethod
    def _load_objects_to_cache(cls, key, objects, serializer):
        conn = RedisClient.get_connection()

        serialized_list = []

        for obj in objects:
            serialized_data = serializer.serialize(obj)
            serialized_list.append(serialized_data)

        # 注意 N+1 queries问题：不要写在上面循环里一个一个rpush，每次rpush都是一次redis访问
        # 而是先构建好list，再rpush整个list
        if serialized_list:
            conn.rpush(key, *serialized_list)
            conn.expire(key, settings.REDIS_KEY_EXPIRE_TIME)

    @classmethod
    def load_objects(cls, key, lazy_load_objects, serializer=DjangoModelSerializer):
        # 最多只 cache REDIS_LIST_LENGTH_LIMIT 那么多个 objects
        # 超过这个限制的 objects，就去数据库里读取。一般这个限制会比较大，比如 200
        # 因此翻页翻到 200 的用户访问量会比较少，从数据库读取也不是大问题
        # 在load和push就截断，提高效率
        conn = RedisClient.get_connection()

        # 如果在 cache 里存在，则直接拿出来，然后返回
        # cache hit
        if conn.exists(key):
            serialized_list = conn.lrange(key, 0, -1)
            objects = []
            for serialized_data in serialized_list:
                deserialized_obj = serializer.deserialize(serialized_data)
                objects.append(deserialized_obj)
            return objects

        # 如果cache里没有，就把所有的objects写入cache
        # cache miss
        # 最多只 cache REDIS_LIST_LENGTH_LIMIT 那么多个 objects
        # 超过这个限制的 objects，就去数据库里读取。一般这个限制会比较大，比如 1000
        # 因此翻页翻到 1000 的用户访问量会比较少，从数据库读取也不是大问题
        objects = lazy_load_objects(settings.REDIS_LIST_LENGTH_LIMIT)
        cls._load_objects_to_cache(key, objects, serializer)
        # 转换为 list 的原因是保持返回类型的统一，因为存在 redis 里的数据是 list 的形式
        return list(objects)

    @classmethod
    def push_object(cls, key, obj, lazy_load_objects):
        conn = RedisClient.get_connection()
        if isinstance(obj, HBaseModel):
            serializer = HBaseModelSerializer
        else:
            serializer = DjangoModelSerializer

        # 如果在 cache 里存在，直接把 obj 放在 list 的最前面，然后 trim 一下长度
        if conn.exists(key):
            serialized_data = serializer.serialize(obj)
            conn.lpush(key, serialized_data)
            conn.ltrim(key, 0, settings.REDIS_LIST_LENGTH_LIMIT - 1)
            return

        # 如果 key 不存在，直接从数据库里 load, 回填到cache
        # 就不走单个 push 的方式加到 cache 里了
        objects = lazy_load_objects(settings.REDIS_LIST_LENGTH_LIMIT)
        cls._load_objects_to_cache(key, objects, serializer)

    @classmethod
    def get_count_key(cls, obj, attr):
        return '{}.{}:{}'.format(obj.__class__.__name__, attr, obj.id)

    @classmethod
    def incr_count(cls, obj, attr):
        conn = RedisClient.get_connection()
        key = cls.get_count_key(obj, attr)

        if not conn.exists(key):
            # back fill cache from db
            # 不执行+1操作，因为调用incr_count之前db里的数据已经+1过了
            obj.refresh_from_db()
            conn.set(key, getattr(obj, attr))
            conn.expire(key, settings.REDIS_KEY_EXPIRE_TIME)
            return getattr(obj, attr)
        return conn.incr(key)

    @classmethod
    def decr_count(cls, obj, attr):
        conn = RedisClient.get_connection()
        key = cls.get_count_key(obj, attr)
        if not conn.exists(key):
            obj.refresh_from_db()
            conn.set(key, getattr(obj, attr))
            conn.expire(key, settings.REDIS_KEY_EXPIRE_TIME)
            return getattr(obj, attr)
        return conn.decr(key)

    @classmethod
    def get_count(cls, obj, attr):
        conn = RedisClient.get_connection()
        key = cls.get_count_key(obj, attr)
        count = conn.get(key)
        if count is not None:
            return int(count)

        obj.refresh_from_db()
        count = getattr(obj, attr)
        conn.set(key, count)
        return count
