from rest_framework import serializers

from .models import Department, DepartmentUser
from users.models import Employee


class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ["name", "job_title"]


class DepartmentEmployeeSerializer(serializers.ModelSerializer):
    employee = MemberSerializer()

    class Meta:
        model = DepartmentUser
        fields = ["employee", "is_head", "is_current"]


class DepartmentSerializer(serializers.ModelSerializer):

    members = DepartmentEmployeeSerializer(many=True)

    class Meta:
        model = Department
        fields = ["id", "department_id", "name", "parent_department_id", "members"]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.parent_department:
            representation["parent_department_id"] = (
                instance.parent_department.department_id
            )  # Or serialize as needed
        return representation


class DepartmentListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Department
        fields = ["id", "department_id", "name", "parent_department_id", "is_deleted"]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.parent_department:
            representation["parent_department_id"] = (
                instance.parent_department.department_id
            )  # Or serialize as needed
        return representation
