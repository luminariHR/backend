from rest_framework import serializers
from django.utils import timezone
from django.db.models import Q
from users.models import Employee
from users.serializers import EmployeeSerializer
from .models import Mentor, Mentee, Match, Session


class MentorSerializer(serializers.ModelSerializer):
    new_candidate_id = serializers.IntegerField(write_only=True)
    employee = EmployeeSerializer(read_only=True)

    class Meta:
        model = Mentor
        fields = ["id", "created_at", "updated_at", "new_candidate_id", "employee"]

    def validate_new_candidate_id(self, value):
        if not Employee.objects.filter(id=value).exists():
            raise serializers.ValidationError("존재하지 않는 유저입니다.")
        return value

    def create(self, validated_data):
        employee_id = validated_data.pop("new_candidate_id")
        if Mentor.objects.filter(employee_id=employee_id).exists():
            raise serializers.ValidationError("이 유저는 이미 멘토입니다.")

        # 기존의 멘티 객체가 있다면 삭제
        today = timezone.now().date()
        if Match.objects.filter(
            Q(mentee_id=employee_id) & Q(end_date__gte=today)
        ).exists():
            raise serializers.ValidationError(
                "아직 진행 중인 멘토링이 있습니다. 종료 후, 변경해주세요."
            )
        Mentee.objects.filter(employee_id=employee_id).delete()

        # 멘토 객체 생성
        mentor = Mentor.objects.create(employee_id=employee_id)
        return mentor

    def delete(self, instance):
        today = timezone.now().date()
        if Match.objects.filter(
            Q(mentor=instance.employee) & Q(end_date__gte=today)
        ).exists():
            raise serializers.ValidationError(
                "아직 진행 중인 멘토링이 있습니다. 종료 후, 삭제해주세요."
            )
        instance.delete()


class MenteeSerializer(serializers.ModelSerializer):
    new_candidate_id = serializers.IntegerField(write_only=True)
    employee = EmployeeSerializer(read_only=True)

    class Meta:
        model = Mentee
        fields = ["id", "created_at", "updated_at", "new_candidate_id", "employee"]

    def validate_new_candidate_id(self, value):
        if not Employee.objects.filter(id=value).exists():
            raise serializers.ValidationError("존재하지 않는 유저입니다.")
        return value

    def create(self, validated_data):
        employee_id = validated_data.pop("new_candidate_id")
        if Mentee.objects.filter(employee_id=employee_id).exists():
            raise serializers.ValidationError("이 유저는 이미 멘티입니다.")

        # 기존의 멘토 객체가 있다면 삭제
        today = timezone.now().date()
        if Match.objects.filter(
            Q(mentor_id=employee_id) & Q(end_date__gte=today)
        ).exists():
            raise serializers.ValidationError(
                "아직 진행 중인 멘토링이 있습니다. 종료 후, 변경해주세요."
            )
        Mentor.objects.filter(employee_id=employee_id).delete()

        # 멘티 객체 생성
        mentee = Mentee.objects.create(employee_id=employee_id)
        return mentee

    def delete(self, instance):
        today = timezone.now().date()
        if Match.objects.filter(
            Q(mentee=instance.employee) & Q(end_date__gte=today)
        ).exists():
            raise serializers.ValidationError(
                "아직 진행 중인 멘토링이 있습니다. 종료 후, 삭제해주세요."
            )
        instance.delete()


class SessionSerializer(serializers.ModelSerializer):
    match_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Session
        fields = [
            "match_id",
            "id",
            "created_at",
            "updated_at",
            "date",
            "note",
            "start_time",
            "end_time",
        ]

    def validate(self, data):
        match_id = data["match_id"]
        if not Match.objects.filter(id=match_id).exists():
            raise serializers.ValidationError("존재하지 않는 멘토 / 멘티 매치입니다.")
        match = Match.objects.get(id=match_id)
        if not (match.start_date <= data["date"] <= match.end_date):
            raise serializers.ValidationError(
                f"멘토링 세션은 {match.start_date} ~ {match.end_date} 사이에 진행되어야 합니다."
            )
        return data

    def create(self, validated_data):
        match_id = validated_data.pop("match_id")
        start_time = validated_data.pop("start_time")
        end_time = validated_data.pop("end_time")
        date = validated_data.pop("date")
        note = validated_data.pop("note", "")
        session = Session.objects.create(
            match_id=match_id,
            start_time=start_time,
            end_time=end_time,
            date=date,
            note=note,
        )
        return session


class MatchSerializer(serializers.ModelSerializer):
    mentor_employee_id = serializers.IntegerField(write_only=True)
    mentee_employee_id = serializers.IntegerField(write_only=True)
    mentor = EmployeeSerializer(read_only=True)
    mentee = EmployeeSerializer(read_only=True)
    sessions = SessionSerializer(many=True, read_only=True)

    class Meta:
        model = Match
        fields = [
            "id",
            "created_at",
            "updated_at",
            "mentor_employee_id",
            "mentee_employee_id",
            "mentor",
            "mentee",
            "start_date",
            "end_date",
            "sessions",
        ]

    def validate(self, data):
        mentor_employee_id = data["mentor_employee_id"]
        mentee_employee_id = data["mentee_employee_id"]
        today = timezone.now().date()

        if not Employee.objects.filter(id=mentor_employee_id).exists():
            raise serializers.ValidationError("존재하지 않는 멘토입니다.")
        if not Employee.objects.filter(id=mentee_employee_id).exists():
            raise serializers.ValidationError("존재하지 않는 멘티입니다.")
        if not Mentor.objects.filter(employee_id=mentor_employee_id).exists():
            raise serializers.ValidationError("존재하지 않는 멘토입니다.")
        if not Mentee.objects.filter(employee_id=mentee_employee_id).exists():
            raise serializers.ValidationError("존재하지 않는 멘티입니다.")
        if Match.objects.filter(
            Q(mentor_id=mentor_employee_id) & Q(end_date__gte=today)
        ).exists():
            raise serializers.ValidationError("이미 매칭이 된 멘토입니다.")
        if Match.objects.filter(
            Q(mentee_id=mentee_employee_id) & Q(end_date__gte=today)
        ).exists():
            raise serializers.ValidationError("이미 매칭이 된 멘티입니다.")

        return data

    def create(self, validated_data):
        mentor_employee_id = validated_data.pop("mentor_employee_id")
        mentee_employee_id = validated_data.pop("mentee_employee_id")
        start_date = validated_data.pop("start_date")
        end_date = validated_data.pop("end_date")
        mentor = Employee.objects.get(id=mentor_employee_id)
        mentee = Employee.objects.get(id=mentee_employee_id)
        match = Match.objects.create(
            mentor=mentor, mentee=mentee, start_date=start_date, end_date=end_date
        )
        return match
