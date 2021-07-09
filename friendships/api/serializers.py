from accounts.api.serializers import UserSerializerForFriendship
from django.contrib.auth.models import User
from friendships.models import Friendship
from friendships.services import FriendshipService
from rest_framework import serializers
from rest_framework.exceptions import ValidationError


class FollowingUserIdSetMixin:

    @property
    def following_user_id_set(self: serializers.ModelSerializer):
        if self.context['request'].user.is_anonymous:
            return {}
        if hasattr(self, '_cached_following_user_id_set'):
            return self._cached_following_user_id_set
        user_id_set = FriendshipService.get_following_user_id_set(
            self.context['request'].user.id,
        )
        setattr(self, '_cached_following_user_id_set', user_id_set)
        return user_id_set


class FollowerSerializer(serializers.ModelSerializer, FollowingUserIdSetMixin):
    # 可以通过 source=xxx 指定去访问每个 model instance 的 xxx 方法
    # 即 model_instance.xxx 来获得数据
    # https://www.django-rest-framework.org/api-guide/serializers/#specifying-fields-explicitly
    user = UserSerializerForFriendship(source='cached_from_user')
    created_at = serializers.DateTimeField()
    has_followed = serializers.SerializerMethodField()

    class Meta:
        model = Friendship
        fields = ('user', 'created_at', 'has_followed',)

    def get_has_followed(self, obj):
        # if self.context['request'].user.is_anonymous:
        #     return False
        # # <TODO> 这个部分会对每个 object 都去执行一次 SQL 查询，速度会很慢，如何优化呢？
        # # 我们将在后序的课程中解决这个问题
        # return FriendshipService.has_followed(self.context['request'].user, obj.from_user)
        return obj.from_user_id in self.following_user_id_set

class FollowingSerializer(serializers.ModelSerializer, FollowingUserIdSetMixin):
    user = UserSerializerForFriendship(source='cached_to_user')
    created_at = serializers.DateTimeField()
    has_followed = serializers.SerializerMethodField()

    class Meta:
        model = Friendship
        fields = ('user', 'created_at', 'has_followed',)

    def get_has_followed(self, obj):
        # if self.context['request'].user.is_anonymous:
        #     return False
        # # <TODO> 这个部分会对每个 object 都去执行一次 SQL 查询，速度会很慢，如何优化呢？
        # # 我们将在后序的课程中解决这个问题
        # return FriendshipService.has_followed(self.context['request'].user, obj.to_user)
        return obj.to_user_id in self.following_user_id_set


class FriendshipSerializerForCreate(serializers.ModelSerializer):
    from_user_id = serializers.IntegerField()
    to_user_id = serializers.IntegerField()

    class Meta:
        model = Friendship
        fields = ('from_user_id', 'to_user_id')

    def validate(self, attrs):
        if attrs['from_user_id'] == attrs['to_user_id']:
            raise ValidationError({
                'message': 'You cannot follow yourself.',
            })
        if not User.objects.filter(id=attrs['to_user_id']).exists():
            raise ValidationError({
                'message': 'You cannot follow a non-exist user.',
            })
        if Friendship.objects.filter(
            from_user_id=attrs['from_user_id'],
            to_user_id=attrs['to_user_id'],
        ).exists():
            raise ValidationError({
                'message': 'You have already followed this user',
            })
        return attrs

    def create(self, validated_data):
        return Friendship.objects.create(
            from_user_id=validated_data['from_user_id'],
            to_user_id=validated_data['to_user_id'],
        )