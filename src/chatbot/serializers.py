from rest_framework import serializers
from .models import ChatbotMessage, ChatbotDocument


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatbotMessage
        fields = "__all__"
        read_only_fields = ["author", "created_at", "updated_at", "answer"]


class ChatbotDocumentSerializer(serializers.ModelSerializer):

    class Meta:
        model = ChatbotDocument
        fields = ["id", "name", "description", "file", "category"]
