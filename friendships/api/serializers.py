from rest_framework.exceptions import ValidationError
from friendships.models import Friendship
from rest_framework import serializers
from accounts.api.serializers import UserSerializerForFriendship
from django.contrib.auth.models import User


class FollowerSerializer(serializers.ModelSerializer):
    # 可以通过 source=xxx 指定去访问每个 model instance 的 xxx 方法
    # 即 model_instance.xxx 来获得数据
    # https://www.django-rest-framework.org/api-guide/serializers/#specifying-fields-explicitly
    user = UserSerializerForFriendship(source='from_user')
    # created_at = serializers.DateTimeField()

    class Meta:
        model = Friendship
        fields = ('user', 'created_at')


class FollowingSerializer(serializers.ModelSerializer):
    user = UserSerializerForFriendship(source='to_user')

    class Meta:
        model = Friendship
        fields = ('user', 'created_at')


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