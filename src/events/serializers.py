from django.core.exceptions import ValidationError
from rest_framework import serializers
from .models import Event


class EventSerializer(serializers.ModelSerializer):

    class Meta:
        model = Event
        fields = "__all__"
        read_only_fields = ["author"]

    def validate(self, data):
        instance = Event(**data)
        try:
            instance.clean()
        except ValidationError as e:
            raise serializers.ValidationError(e.message)

        return data

    def create(self, validated_data):
        request = self.context["request"]
        # 작성자는 무조건 본인으로 지정
        validated_data["author"] = request.user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        request = self.context["request"]
        # 작성자는 무조건 본인으로 지정
        validated_data["author"] = request.user
        return super().update(instance, validated_data)

    def delete(self, instance):
        instance.delete()
