from rest_framework import serializers
from departments.models import Department
from users.models import Employee
from .models import Appointment
import datetime


class AdminAppointmentSerializer(serializers.ModelSerializer):

    employee_id = serializers.IntegerField()
    new_department_id = serializers.IntegerField()
    effective_date = serializers.DateField(default=datetime.date.today)

    class Meta:
        model = Appointment
        fields = [
            "id",
            "employee",
            "new_job_title",
            "new_department",
            "is_department_head",
            "effective_date",
            "note",
            "employee_id",
            "new_department_id",
        ]
        read_only_fields = ["employee", "new_department"]

    def validate(self, data):
        employee_id = data.get("employee_id", None)
        new_job_title = data.get("new_job_title", None)
        new_department_id = data.get("new_department_id", None)
        effective_date = data.get("effective_date", None)
        is_department_head = data.get("is_department_head", None)
        employee = Employee.objects.get(id=employee_id)
        new_department = Department.objects.get(id=new_department_id)

        if new_job_title and new_department_id:
            if (
                employee.job_title == new_job_title
                and employee.department.id == new_department_id
                and (new_department.head == employee) == is_department_head
            ):
                raise serializers.ValidationError(
                    "동일한 부서, 직책으로 발령낼 수 없습니다."
                )
        if new_department.is_deleted:
            raise serializers.ValidationError(
                {"new_department": "삭제된 부서로 발령 낼 수 없습니다."}
            )
        data["new_department"] = new_department
        data["employee"] = employee
        if effective_date and effective_date != datetime.date.today():
            raise serializers.ValidationError(
                {"effective_date": "현재는 당일 인사 발령 밖에 지원하지 않습니다."}
            )
        return data

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.new_department:
            representation["new_department_id"] = instance.new_department.department_id
        return representation

    def create(self, validated_data):
        request = self.context["request"]
        validated_data.pop("new_department_id", None)
        return super().create(validated_data)
