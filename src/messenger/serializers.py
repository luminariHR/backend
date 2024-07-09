from rest_framework import serializers
from .models import ChatRoom, ChatRoomParticipant, Message

class ChatRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatRoom
        fields = ['id', 'name', 'participants']

class ChatRoomParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatRoomParticipant
        fields = ['id', 'employee', 'chat_room', 'joined_at', 'left_at']

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'chat_room', 'sender', 'content', 'timestamp']
