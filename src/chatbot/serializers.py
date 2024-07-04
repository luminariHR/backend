from rest_framework import serializers
from .models import Message


class MessageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Message
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


from rest_framework import serializers
from .models import ChatbotDocument


class ChatbotDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatbotDocument
        fields = ["id", "title", "file_path", "created_at"]
