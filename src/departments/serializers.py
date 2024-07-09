from rest_framework import serializers

from .models import Department
from users.models import Employee


class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ["id", "employee_id", "name", "job_title"]


class DepartmentSerializer(serializers.ModelSerializer):

    members = MemberSerializer(many=True)
    head = MemberSerializer()

    class Meta:
        model = Department
        fields = [
            "id",
            "department_id",
            "name",
            "address",
            "parent_department_id",
            "members",
            "head",
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.parent_department:
            representation["parent_department_id"] = (
                instance.parent_department.department_id
            )  # Or serialize as needed
        return representation


class DepartmentListSerializer(serializers.ModelSerializer):

    head = MemberSerializer()

    class Meta:
        model = Department
        fields = [
            "id",
            "department_id",
            "name",
            "head",
            "address",
            "parent_department_id",
            "is_deleted",
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.parent_department:
            representation["parent_department_id"] = (
                instance.parent_department.department_id
            )
        return representation


class AdminDepartmentSerializer(serializers.ModelSerializer):

    parent_department_id = serializers.CharField(max_length=50)

    class Meta:
        model = Department
        fields = [
            "id",
            "department_id",
            "name",
            "address",
            "is_deleted",
            "parent_department_id",
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.parent_department:
            representation["parent_department_id"] = (
                instance.parent_department.department_id
            )
        return representation

    def validate(self, data):
        parent_department_id = data.get("parent_department_id", None)
        if self.instance:
            department = self.instance
        else:
            department = Department(department_id=data.get("department_id"))

        if parent_department_id:
            try:
                parent_department = Department.objects.get(
                    department_id=parent_department_id
                )
                if self._creates_cycle(department, parent_department):
                    raise serializers.ValidationError(
                        "하위 부서가 상위 부서가 될 수 없습니다."
                    )
                data["parent_department"] = parent_department
            except Department.DoesNotExist:
                raise serializers.ValidationError(
                    {"parent_department_id": "존재하지 않는 상위 부서입니다."}
                )

        return data

    @staticmethod
    def _creates_cycle(department, parent_department):
        if department == parent_department:
            return True
        current = parent_department
        while current:
            if current == department:
                return True
            current = current.parent_department
        return False

    def create(self, validated_data):
        request = self.context["request"]
        validated_data.pop("parent_department_id", None)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        request = self.context["request"]
        validated_data.pop("parent_department_id", None)
        return super().update(instance, validated_data)
