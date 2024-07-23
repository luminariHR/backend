from rest_framework import serializers
from users.models import Employee
from .models import Mentor, Mentee, Match


class MentorSerializer(serializers.ModelSerializer):
    employees_id = serializers.IntegerField(write_only=True)
    employee_id = serializers.IntegerField(source="employee.id", read_only=True)

    class Meta:
        model = Mentor
        fields = ["employees_id", "employee_id"]

    def validate_employees_id(self, value):
        if not Employee.objects.filter(id=value).exists():
            raise serializers.ValidationError("Employee with this ID does not exist.")
        return value

    def create(self, validated_data):
        employee_id = validated_data.pop("employees_id")
        employee = Employee.objects.get(id=employee_id)

        # 기존의 멘티 객체가 있다면 삭제
        Mentee.objects.filter(employee=employee).delete()

        # 멘토 객체 생성 또는 업데이트
        mentor, created = Mentor.objects.update_or_create(
            employee=employee, defaults={}
        )
        return mentor


class MenteeSerializer(serializers.ModelSerializer):
    employees_id = serializers.IntegerField(write_only=True)
    employee_id = serializers.IntegerField(source="employee.id", read_only=True)

    class Meta:
        model = Mentee
        fields = ["employees_id", "employee_id"]

    def validate_employees_id(self, value):
        if not Employee.objects.filter(id=value).exists():
            raise serializers.ValidationError("Employee with this ID does not exist.")
        return value

    def create(self, validated_data):
        employee_id = validated_data.pop("employees_id")
        employee = Employee.objects.get(id=employee_id)

        # 기존의 멘토 객체가 있다면 삭제
        Mentor.objects.filter(employee=employee).delete()

        # 멘티 객체 생성 또는 업데이트
        mentee, created = Mentee.objects.update_or_create(
            employee=employee, defaults={}
        )
        return mentee


class MatchSerializer(serializers.ModelSerializer):
    mentor_employee_id = serializers.IntegerField(write_only=True)
    mentee_employee_id = serializers.IntegerField(write_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    mentor_id = serializers.IntegerField(source="mentor.id", read_only=True)
    mentee_id = serializers.IntegerField(source="mentee.id", read_only=True)

    class Meta:
        model = Match
        fields = [
            "mentor_employee_id",
            "mentee_employee_id",
            "created_at",
            "mentor_id",
            "mentee_id",
        ]

    def validate(self, data):
        mentor_employee_id = data["mentor_employee_id"]
        mentee_employee_id = data["mentee_employee_id"]

        if not Employee.objects.filter(id=mentor_employee_id).exists():
            raise serializers.ValidationError(
                "Mentor with this employee ID does not exist."
            )
        if not Employee.objects.filter(id=mentee_employee_id).exists():
            raise serializers.ValidationError(
                "Mentee with this employee ID does not exist."
            )
        if not Mentor.objects.filter(employee_id=mentor_employee_id).exists():
            raise serializers.ValidationError("This Employee is not a Mentor.")
        if not Mentee.objects.filter(employee_id=mentee_employee_id).exists():
            raise serializers.ValidationError("This Employee is not a Mentee.")
        if Match.objects.filter(mentor_id=mentor_employee_id).exists():
            raise serializers.ValidationError("This Mentor is already matched.")
        if Match.objects.filter(mentee_id=mentee_employee_id).exists():
            raise serializers.ValidationError("This Mentee is already matched.")

        return data

    def create(self, validated_data):
        mentor_employee_id = validated_data.pop("mentor_employee_id")
        mentee_employee_id = validated_data.pop("mentee_employee_id")
        mentor = Employee.objects.get(id=mentor_employee_id)
        mentee = Employee.objects.get(id=mentee_employee_id)
        match = Match.objects.create(mentor=mentor, mentee=mentee)
        return match
