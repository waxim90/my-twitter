from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from comments.api.serializers import (
    CommentSerializerForCreate,
    CommentSerializer,
)
from comments.models import Comment


class CommentViewSet(viewsets.GenericViewSet):
    """
    只实现 list, create, update, destroy 的方法
    不实现 retrieve（查询单个 comment） 的方法，因为没这个需求
    """
    serializer_class = CommentSerializerForCreate
    queryset = Comment.objects.all()

    # permission检测:
    # 自定义方法：可以用@action 里加 permission_class=
    # 默认方法：要用get_permissions()方法
    # POST /api/comments/     -> create
    # GET /api/comments/      -> list
    # GET /api/comments/1/    -> retrieve
    # DELETE /api/comments/1/ -> destroy
    # PATCH /api/comments/1/  -> partial_update
    # PUT /api/comments/1/    -> update
    def get_permissions(self):
        # 注意要加用 AllowAny() / IsAuthenticated() 实例化出对象
        # 而不是 AllowAny / IsAuthenticated 这样只是一个类名
        if self.action == 'create':
            return [IsAuthenticated()]
        return [AllowAny()]

    def create(self, request, *args, **kwargs):
        # 这里是直接构造一个data dict，里面包含我们create要用到的参数
        # 也可以像之前一样， 把request当成context传进去：
        # serializer = CommentSerializerForCreate(
        #     data=request.data,
        #     context={'request': request},
        # )
        data = {
            'user_id': request.user.id,
            'tweet_id': request.data.get('tweet_id'),
            'content': request.data.get('content'),
        }
        # 注意这里必须要加 'data=' 来指定参数是传给 data 的
        # 因为默认的第一个参数是 instance
        serializer = CommentSerializerForCreate(data=data)
        # serializer = CommentSerializerForCreate(
        #     data=request.data,
        #     context={'request': request},
        # )
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': 'Please check input.',
                'errors': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)

        # save 方法会触发 serializer 里的 create 方法，点进 save 的具体实现里可以看到
        comment = serializer.save()
        return Response(
            CommentSerializer(comment).data,
            status=status.HTTP_201_CREATED,
        )

