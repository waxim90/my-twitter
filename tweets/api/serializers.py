from rest_framework import serializers
from comments.api.serializers import CommentSerializer
from tweets.models import Tweet
from accounts.api.serializers import UserSerializerForTweet


class TweetSerializer(serializers.ModelSerializer):
    # 为了解析user其他数据 例如username等等
    user = UserSerializerForTweet()

    class Meta:
        model = Tweet
        fields = ('id', 'user', 'created_at', 'content')


class TweetSerializerWithComments(TweetSerializer):
    comments = CommentSerializer(source='comment_set', many=True)
    # 使用 serialziers.SerializerMethodField 的方式实现 comments
    # comments = serializers.SerializerMethodField()
    #
    # def get_comments(self, obj):
    #     return CommentSerializer(obj.comment_set.all(), many=True).data

    class Meta:
        model = Tweet
        fields = ('id', 'user', 'created_at', 'content', 'comments')


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
