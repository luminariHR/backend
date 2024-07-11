from rest_framework import viewsets
from .models import ChatRoom, ChatRoomParticipant, Message
from .serializers import ChatRoomSerializer, MessageSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from collections import Counter
from users.models import Employee


class ChatRoomViewSet(viewsets.ModelViewSet):
    queryset = ChatRoom.objects.all()
    serializer_class = ChatRoomSerializer

    # @action(detail=True, methods=["post"])
    # def join(self, request, pk=None, *args, **kwargs):
    #     chat_room = self.get_object()
    #     employee = request.user
    #     try:
    #         ChatRoomParticipant.objects.get(
    #             employee=employee, chat_room=chat_room, left_at__isnull=True
    #         )
    #     except ChatRoomParticipant.DoesNotExist:
    #         ChatRoomParticipant.objects.create(employee=employee, chat_room=chat_room)
    #     except ChatRoomParticipant.MultipleObjectsReturned:
    #         participants = ChatRoomParticipant.objects.filter(
    #             employee=employee, chat_room=chat_room, left_at__isnull=True
    #         )
    #         participants.exclude(pk=participants.first().pk).delete()
    #     return Response(status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"])
    def create_or_get_chat_room(self, request, *args, **kwargs):
        participants_ids = request.data.get("participants", [])
        if not participants_ids:
            return Response(
                {"error": "Participants are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user_id = request.user.pk
        if user_id not in participants_ids:
            participants_ids.append(user_id)

        if len(participants_ids) < 2:
            return Response(
                {"error": "At least two participants are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        chat_room = self._create_or_get_chat_room(participants_ids)
        serializer = self.get_serializer(chat_room)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def _create_or_get_chat_room(self, participants_ids):
        existing_chat_room = self.chat_room_exists(participants_ids)
        if existing_chat_room:
            return existing_chat_room
        new_chat_room = ChatRoom.objects.create(name=f"chatroom_{participants_ids}")
        for participant_id in participants_ids:
            ChatRoomParticipant.objects.create(
                chat_room=new_chat_room, employee_id=participant_id
            )
        return new_chat_room

    def chat_room_exists(self, participants_ids):
        chat_rooms = ChatRoom.objects.all().order_by("-created_at")
        for chat_room in chat_rooms:
            chat_room_participants = ChatRoomParticipant.objects.filter(
                chat_room=chat_room, left_at__isnull=True
            ).values_list("employee_id", flat=True)
            if Counter(chat_room_participants) == Counter(participants_ids):
                return chat_room
        return None

    @action(detail=True, methods=["post"])
    def invite_user(self, request, pk=None, *args, **kwargs):
        chat_room = self.get_object()
        chat_room_participants = ChatRoomParticipant.objects.filter(
            chat_room=chat_room
        ).values_list("employee_id", flat=True)
        print(chat_room_participants)
        user_id = request.data.get("user_id")
        if not user_id:
            return Response(
                {"error": "User ID is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            Employee.objects.get(pk=user_id)
        except Employee.DoesNotExist:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )

        if user_id in chat_room_participants:
            return Response(
                {"error": "User is already in the chat room"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        ChatRoomParticipant.objects.create(chat_room=chat_room, employee_id=user_id)
        serializer = self.get_serializer(chat_room)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def leave(self, request, pk=None, *args, **kwargs):
        chat_room = self.get_object()
        employee = request.user
        participant = ChatRoomParticipant.objects.filter(
            employee=employee, chat_room=chat_room, left_at__isnull=True
        ).first()
        if participant:
            participant.delete()
        return Response(status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"])
    def get_chat_history(self, request, pk=None, *args, **kwargs):
        try:
            chat_room = self.get_object()
            employee = request.user
            participant = ChatRoomParticipant.objects.filter(
                employee=employee, chat_room=chat_room, left_at__isnull=True
            ).first()

            chat_history = Message.objects.filter(
                Q(chat_room=chat_room) & Q(timestamp__gte=participant.joined_at)
            ).order_by("timestamp")

            serializer = MessageSerializer(chat_history, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
