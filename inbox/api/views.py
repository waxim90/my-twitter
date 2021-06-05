from notifications.models import Notification
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from inbox.api.serializers import NotificationSerializer


class NotificationViewSet(
    viewsets.GenericViewSet,
    viewsets.mixins.ListModelMixin,
):
    permission_classes = (IsAuthenticated,)
    serializer_class = NotificationSerializer
    # ListModelMixin 里 list方法会用到， 来只list unread/read notifications
    filterset_fields = ('unread',)

    def get_queryset(self):
        return Notification.objects.all().filter(recipient=self.request.user)
        # return self.request.user.notifications.all()

    # GET /api/notifications/unread-count/
    # 如果不指定 url_path, 默认地址为 /api/notifications/unread_count/
    # url里有下划线不符合rest, 所以要指定 url_path='unread-count'
    @action(methods=['GET'], detail=False, url_path='unread-count')
    def unread_count(self, request, *args, **kwargs):
        count = self.get_queryset().filter(unread=True).count()
        return Response({'unread_count': count}, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=False, url_path='mark-all-as-read')
    def mark_all_as_read(self, request, *args, **kwargs):
        updated_count = self.get_queryset().filter(unread=True).update(unread=False)
        return Response({'marked_count': updated_count}, status=status.HTTP_200_OK)