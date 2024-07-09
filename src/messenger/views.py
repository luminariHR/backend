from rest_framework import viewsets
from .models import ChatRoom, ChatRoomParticipant, Message
from .serializers import ChatRoomSerializer, ChatRoomParticipantSerializer, MessageSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone

class ChatRoomViewSet(viewsets.ModelViewSet):
    queryset = ChatRoom.objects.all()
    serializer_class = ChatRoomSerializer

    @action(detail=True, methods=['post'])
    def join(self, request, pk=None, *args, **kwargs):
        chat_room = self.get_object()
        employee = request.user
        # participant, created = ChatRoomParticipant.objects.get_or_create(employee=employee, chat_room=chat_room, left_at__isnull=True)
        # if not created:
        #     participant.left_at = None
        #     participant.save()
        # else:
        #     ChatRoomParticipant.objects.create(employee=employee, chat_room=chat_room)
            
        try:
            participant = ChatRoomParticipant.objects.get(employee=employee, chat_room=chat_room, left_at__isnull=True)
        except ChatRoomParticipant.MultipleObjectsReturned:
            participant = ChatRoomParticipant.objects.filter(employee=employee, chat_room=chat_room, left_at__isnull=True).first()

        if not participant:
            participant = ChatRoomParticipant.objects.create(employee=employee, chat_room=chat_room)      
        return Response(status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def leave(self, request, pk=None, *args, **kwargs):
        chat_room = self.get_object()
        employee = request.user
        participant = ChatRoomParticipant.objects.filter(employee=employee, chat_room=chat_room, left_at__isnull=True).first()
        if participant:
            participant.left_at = timezone.now()
            participant.save()
        return Response(status=status.HTTP_200_OK)

class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
