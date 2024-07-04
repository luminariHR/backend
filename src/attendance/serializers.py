from rest_framework import serializers
from .models import Attendance


class AttendanceSerializer(serializers.ModelSerializer):

    hours_worked = serializers.SerializerMethodField()

    class Meta:
        model = Attendance
        fields = "__all__"
        read_only_fields = [
            "employee",
            "date",
            "is_late",
            "is_early_leave",
            "is_excused",
            "hours_worked",
            "overtime",
            "hr_note",
        ]

    def create(self, validated_data):
        request = self.context["request"]
        # 대상자는 무조건 본인으로 지정
        validated_data["employee"] = request.user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        data = {}
        if "clock_out" in validated_data:
            data["clock_out"] = validated_data.get("clock_out")
        elif "clock_in_note" in validated_data:
            data["clock_in_note"] = validated_data.get("clock_in_note")
        if "clock_out_note" in validated_data:
            data["clock_out_note"] = validated_data.get("clock_out_note")
        return super().update(instance, data)

    def get_hours_worked(self, obj):
        return obj.get_hours_worked()


class AdminAttendanceSerializer(serializers.ModelSerializer):
    pass
