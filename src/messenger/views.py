from rest_framework import viewsets
from .models import ChatRoom, ChatRoomParticipant, Message
from .serializers import ChatRoomSerializer, ChatRoomParticipantSerializer, MessageSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.db.models import Q

class ChatRoomViewSet(viewsets.ModelViewSet):
    queryset = ChatRoom.objects.all()
    serializer_class = ChatRoomSerializer

    @action(detail=True, methods=['post'])
    def join(self, request, pk=None, *args, **kwargs):
        chat_room = self.get_object()
        employee = request.user
            
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
    
    @action(detail=True, methods=['get'])
    def get_chat_history(self, request, pk=None, *args, **kwargs):
        try:
            chat_room = self.get_object()
            employee = request.user
            participant = ChatRoomParticipant.objects.filter(employee=employee, chat_room=chat_room, left_at__isnull=True).first()

            chat_history = Message.objects.filter(
                Q(chat_room=chat_room) &
                Q(timestamp__gte=participant.joined_at)
            ).order_by('timestamp')

            serializer = MessageSerializer(chat_history, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
