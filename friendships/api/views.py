from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from ratelimit.decorators import ratelimit
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from friendships.models import Friendship
from friendships.api.serializers import (
    FollowerSerializer,
    FollowingSerializer,
    FriendshipSerializerForCreate
)
from friendships.services import FriendshipService
from utils.paginations import FriendshipPagination


class FriendshipViewSet(viewsets.GenericViewSet):
    # 我们希望 POST /api/friendships/1/follow 是去 follow user_id=1 的用户
    # 因此这里 queryset 需要是 User.objects.all()
    # 如果是 Friendship.objects.all 的话就会出现 404 Not Found
    # 因为 detail=True 的 actions 会默认先去调用 get_object() 也就是
    # queryset.filter(pk=1) 查询一下这个 object 在不在
    queryset = User.objects.all()
    serializer_class = FriendshipSerializerForCreate
    # 一般来说，不同的 views 所需要的 pagination 规则肯定是不同的，因此一般都需要自定义
    pagination_class = FriendshipPagination

    # GET /api/friendships/1/followers/
    @action(methods=['GET'], detail=True, permission_classes=[AllowAny])
    @method_decorator(ratelimit(key='user_or_ip', rate='3/s', method='GET', block=True))
    def followers(self, request, pk):
        friendships = Friendship.objects.filter(to_user=pk)
        page = self.paginate_queryset(friendships)
        # many=True tell drf that queryset contains multiple items (a list of items)
        serializer = FollowerSerializer(page, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)

    # GET /api/friendships/1/followings
    @action(methods=['GET'], detail=True, permission_classes=[AllowAny])
    @method_decorator(ratelimit(key='user_or_ip', rate='3/s', method='GET', block=True))
    def followings(self, request, pk):
        friendships = Friendship.objects.filter(from_user=pk)
        page = self.paginate_queryset(friendships)
        # many=True tell drf that queryset contains multiple items (a list of items)
        serializer = FollowingSerializer(page, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(methods=['POST'], detail=True, permission_classes=[IsAuthenticated])
    @method_decorator(ratelimit(key='user', rate='10/s', method='POST', block=True))
    def follow(self, request, pk):
        # /api/friendships/<pk>/follow/
        # raise 404 if no user with id=pk
        to_follow_user = self.get_object()

        # 特殊判断重复 follow 的情况（比如前端猛点好多少次 follow)
        # 静默处理，不报错，因为这类重复操作因为网络延迟的原因会比较多，没必要当做错误处理
        # 或者报400
        if FriendshipService.has_followed(request.user.id, to_follow_user.id):
            return Response({
                'success': False,
                'errors': [{'pk': f'You have followed user with id={pk}'}],
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = FriendshipSerializerForCreate(data={
            'from_user_id': request.user.id,
            'to_user_id': to_follow_user.id,
        })
        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)
        instance = serializer.save()
        # 手动invalidate cache 或者利用listener自动调用 invalidate_following_cache
        # FriendshipService.invalidate_following_cache(request.user.id)
        return Response(
            FollowingSerializer(instance, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )

    @action(methods=['POST'], detail=True, permission_classes=[IsAuthenticated])
    @method_decorator(ratelimit(key='user', rate='10/s', method='POST', block=True))
    def unfollow(self, request, pk):
        # raise 404 if no user with id=pk
        unfollow_user = self.get_object()
        # 注意 pk 的类型是 str，所以要做类型转换
        # if request.user.id == int(pk):
        if request.user.id == unfollow_user.id:
            return Response({
                'success': False,
                'message': 'You cannot unfollow yourself',
            }, status=status.HTTP_400_BAD_REQUEST)
        deleted = FriendshipService.unfollow(request.user.id, unfollow_user.id)
        return Response({'success': True, 'deleted': deleted})

    @method_decorator(ratelimit(key='user_or_ip', rate='3/s', method='GET', block=True))
    def list(self, request):
        return Response({'message': 'this is friendships home page'})
