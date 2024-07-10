from rest_framework import serializers
from .models import Message


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ["id", "post", "datetime", "question", "answer"]
        read_only_fields = ["post", "datetime", "answer"]
