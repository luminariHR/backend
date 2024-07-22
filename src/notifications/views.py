from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import NotificationSerializer
from .models import Notification


class NotificationsView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, version):
        context = {"request": request}
        user = self.request.user
        notifications = Notification.objects.filter(receiver=user)
        serializer = NotificationSerializer(notifications, context=context, many=True)
        return Response(serializer.data)


class ReadAllView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, version):
        context = {"request": request}
        user = self.request.user
        notifications = Notification.objects.filter(receiver=user, is_read=False)
        notifications.update(is_read=True)
        return Response({"message": "모든 알림을 읽기 처리 했습니다."})
