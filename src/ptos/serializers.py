from rest_framework import serializers
from departments.models import Department
from users.models import Employee
from django.utils import timezone
from django.db.models import Q
from .models import PTO


class DepartmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Department
        fields = ["id", "name"]


class EmployeeSerializer(serializers.ModelSerializer):

    department = DepartmentSerializer()

    class Meta:
        model = Employee
        fields = [
            "id",
            "employee_id",
            "name",
            "job_title",
            "profile_image",
            "department",
        ]


class PTOEmployeeSerializer(serializers.Serializer):

    id = serializers.IntegerField()
    employee_id = serializers.CharField()
    job_title = serializers.CharField()
    name = serializers.CharField()
    profile_image = serializers.FileField()
    department = DepartmentSerializer()
    start_date = serializers.DateField()
    end_date = serializers.DateField()


class MonthlyPTOSerializer(serializers.Serializer):

    total_count = serializers.IntegerField()
    date = serializers.DateField()


class DailyPTOSerializer(MonthlyPTOSerializer):

    employees = PTOEmployeeSerializer(many=True, read_only=True)


class PTOSerializer(serializers.ModelSerializer):

    employee = EmployeeSerializer(read_only=True)
    authorizer = EmployeeSerializer(read_only=True)

    class Meta:
        model = PTO
        fields = "__all__"
        read_only_fields = ("employee", "authorizer")

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["pto_type"] = instance.get_pto_type_display(instance)
        return representation

    def validate(self, attrs):
        request = self.context["request"]
        user = request.user
        if not user.department:
            raise serializers.ValidationError(
                "부서가 존재하지 않으면 휴가 신청이 불가합니다."
            )
        if "start_date" in attrs and "end_date" in attrs:
            today = timezone.now().date()
            if attrs["start_date"] < today:
                raise serializers.ValidationError(
                    {"start_date": "휴가 시작일이 오늘보다 빠를 수 없습니다."}
                )
            if attrs["end_date"] < today:
                raise serializers.ValidationError(
                    {"end_date": "휴가 종료일이 오늘보다 빠를 수 없습니다."}
                )
            if attrs["start_date"] > attrs["end_date"]:
                raise serializers.ValidationError(
                    {"start_date": "휴가 시작일이 휴가 종료일보다 빨라야 합니다."}
                )

            overlapping_instances = PTO.objects.filter(
                Q(
                    start_date__gte=attrs["start_date"],
                    end_date__lte=attrs["start_date"],
                    employee=user,
                )
                | Q(
                    start_date__gte=attrs["end_date"],
                    end_date__lte=attrs["end_date"],
                    employee=user,
                )
            )
            if overlapping_instances.exists():
                raise serializers.ValidationError(
                    "이미 신청된 휴가와 겹치는 날짜가 포함되어 있습니다."
                )
        return attrs

    def create(self, validated_data):
        request = self.context["request"]
        user = request.user
        # 요청자가 무조건 본인으로 지정
        validated_data["employee"] = user
        # 승인권자는 부서장으로 지정. 부서장 부재 시 선임자가 승인권자로 지정.
        if user.department.head:
            validated_data["authorizer"] = request.user.department.head
        else:
            earliest_member = request.user.department.members.order_by(
                "start_date"
            ).first()
            validated_data["authorizer"] = earliest_member
        return super().create(validated_data)

    def update(self, instance, validated_data):
        request = self.context["request"]
        user = request.user
        # 승인권자만 승인 가능
        if "status" in validated_data and instance.authorizer != user:
            raise serializers.ValidationError(
                "승인권자만 휴가 요청 검토를 할 수 있습니다."
            )
        return super().update(instance, validated_data)
