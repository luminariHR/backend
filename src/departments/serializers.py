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
        fields = [
            "id",
            "department_id",
            "name",
            "address",
            "parent_department_id",
            "members",
        ]

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
        fields = [
            "id",
            "department_id",
            "name",
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

    class Meta:
        model = Department
        fields = [
            "id",
            "department_id",
            "name",
            "address",
            "is_deleted",
            "parent_department",
            "parent_department_id",
        ]
        read_only_fields = ["parent_department"]

    def validate(self, data):
        parent_department_id = data.get("parent_department_id", None)
        department_head_id = data.get("department_head_id", None)

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
                        "하위 부서가 상위 부서가 될 수 없습니다 (사이클)."
                    )
                data["parent_department"] = parent_department
            except Department.DoesNotExist:
                raise serializers.ValidationError(
                    {"parent_department_id": "존재하지 않는 상위 부서입니다."}
                )

        if department_head_id:
            try:
                department_head = Employee.objects.get(id=department_head_id)
                data["department_head"] = department_head
            except Employee.DoesNotExist:
                raise serializers.ValidationError(
                    {"department_head_id": "존재하지 않는 직원입니다."}
                )

        return data

    @staticmethod
    def _creates_cycle(self, department, parent_department):
        if department == parent_department:
            return True
        current = parent_department
        while current:
            if current == department:
                return True
            current = current.parent_department
        return False

    def _set_department_head(self, department, department_head):
        if department_head:
            DepartmentUser.objects.filter(department=department, is_head=True).update(
                is_current=False
            )

            # Set the new department head
            department_user, created = DepartmentUser.objects.get_or_create(
                department=department,
                employee=department_head,
                defaults={"is_head": True, "is_current": True},
            )
            if not created:
                department_user.is_head = True
                department_user.is_current = True
                department_user.save()

    def create(self, validated_data):
        request = self.context["request"]
        validated_data.pop("parent_department_id", None)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data.pop("parent_department_id", None)
        return super().update(instance, validated_data)
