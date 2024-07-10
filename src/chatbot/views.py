from rest_framework import viewsets, permissions
from rest_framework.response import Response
from .models import Message
from .serializers import MessageSerializer
from rest_framework.permissions import IsAuthenticated


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Message.objects.filter(post=user)

    def perform_create(self, serializer):
        serializer.save(post=self.request.user)

    def perform_create(self, serializer):
        # 요청한 사용자를 post 필드로 저장하고, answer 필드에 "응답" 여기에 필요시 랭체인 추가
        serializer.save(post=self.request.user, answer="응답")
