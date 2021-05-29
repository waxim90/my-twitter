from rest_framework import serializers
from comments.api.serializers import CommentSerializer
from likes.api.serializers import LikeSerializer
from tweets.models import Tweet
from accounts.api.serializers import UserSerializerForTweet
from likes.services import LikeService


class TweetSerializer(serializers.ModelSerializer):
    # 为了解析user其他数据 例如username等等
    user = UserSerializerForTweet()
    has_liked = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Tweet
        fields = (
            'id',
            'user',
            'created_at',
            'content',
            'has_liked',
            'likes_count',
            'comments_count',
        )

    def get_has_liked(self, obj):
        return LikeService.has_liked(self.context['request'].user, obj)

    def get_likes_count(self, obj):
        return obj.like_set.count()

    def get_comments_count(self, obj):
        return obj.comment_set.count()


class TweetSerializerForDetail(TweetSerializer):
    comments = CommentSerializer(source='comment_set', many=True)
    likes = LikeSerializer(source='like_set', many=True)
    # 使用 serialziers.SerializerMethodField 的方式实现 comments
    # comments = serializers.SerializerMethodField()
    #
    # def get_comments(self, obj):
    #     return CommentSerializer(obj.comment_set.all(), many=True).data

    class Meta:
        model = Tweet
        fields = (
            'id',
            'user',
            'created_at',
            'content',
            'comments',
            'likes',
            'has_liked',
            'likes_count',
            'comments_count',
        )


class TweetSerializerForCreate(serializers.ModelSerializer):
    content = serializers.CharField(min_length=6, max_length=140)

    class Meta:
        model = Tweet
        fields = ('content',)

    def create(self, validated_data):
        user = self.context['request'].user
        content = validated_data['content']
        tweet = Tweet.objects.create(user=user, content=content)
        return tweet
