from django.contrib.auth.models import Group
from django.conf import settings
from django.db import transaction
from rest_framework import serializers
from .models import Employee
from departments.models import DepartmentUser, Department


class DepartmentSerializer(serializers.ModelSerializer):
    is_head = serializers.BooleanField(read_only=True)

    class Meta:
        model = Department
        fields = ["id", "name", "is_head"]

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if "is_head" in self.context:
            ret["is_head"] = self.context["is_head"]
        return ret


class EmployeeSerializer(serializers.ModelSerializer):
    HR_ADMIN_EXCLUSIVE_FIELDS = [
        "employee_id",
        "email",
        "is_hr_admin",
        "start_date",
        "end_date",
        "job_title",
        "department_id",
        "is_head",
    ]
    is_hr_admin = serializers.BooleanField(write_only=False, required=False)
    department = serializers.SerializerMethodField()
    department_id = serializers.CharField(write_only=True, required=False)
    is_head = serializers.BooleanField(write_only=True, required=False, default=False)

    class Meta:
        model = Employee
        fields = [
            "id",
            "last_name",
            "first_name",
            "email",
            "employee_id",
            "gender",
            "employment_status",
            "job_title",
            "phone_number",
            "start_date",
            "end_date",
            "is_hr_admin",
            "department",
            "department_id",
            "is_head",
        ]

    def is_user_hr_admin(self):
        user = self.context["request"].user
        return user.groups.filter(name=settings.HR_ADMIN_GROUP_NAME).exists()

    def get_department(self, obj):
        department_user = DepartmentUser.objects.filter(
            employee=obj, is_current=True
        ).first()
        if department_user and department_user.department:
            serializer_context = {"is_head": department_user.is_head}
            return DepartmentSerializer(
                department_user.department, context=serializer_context
            ).data
        return None

    @staticmethod
    def add_or_remove_hr_admin_group(is_hr_admin, user):
        if is_hr_admin is True:
            group = Group.objects.get(name=settings.HR_ADMIN_GROUP_NAME)
            group.user_set.add(user)
        elif is_hr_admin is False:
            group = Group.objects.get(name=settings.HR_ADMIN_GROUP_NAME)
            group.user_set.remove(user)

    @staticmethod
    def assign_employee_to_dept(employee, department_id, is_head):

        department = Department.objects.get(department_id=department_id)
        department_user = DepartmentUser.objects.create(
            department=department,
            employee=employee,
            is_head=is_head,
        )
        DepartmentUser.objects.filter(
            employee=department_user.employee, is_current=True
        ).exclude(pk=department_user.pk).update(is_current=False)
        return department_user

    def create(self, validated_data):
        is_hr_admin = validated_data.pop("is_hr_admin", False)
        department_id = validated_data.pop("department_id", None)
        is_head = validated_data.pop("is_head", False)
        with transaction.atomic():
            user = super().create(validated_data)
            if department_id:
                self.assign_employee_to_dept(user, department_id, is_head)
            self.add_or_remove_hr_admin_group(is_hr_admin, user)

        return user

    def update(self, instance, validated_data):
        # HR 관리자가 아닐 경우, HR 관리자 전용 필드 삭제
        if not self.is_user_hr_admin():
            for field in self.HR_ADMIN_EXCLUSIVE_FIELDS:
                validated_data.pop(field, None)
        is_hr_admin = validated_data.pop("is_hr_admin", None)
        department_id = validated_data.pop("department_id", None)
        is_head = validated_data.pop("is_head", False)
        with transaction.atomic():
            instance = super().update(instance, validated_data)
            if department_id:
                self.assign_employee_to_dept(instance, department_id, is_head)
            self.add_or_remove_hr_admin_group(is_hr_admin, instance)
        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["is_hr_admin"] = instance.groups.filter(
            name=settings.HR_ADMIN_GROUP_NAME
        ).exists()
        representation["employment_status"] = instance.get_employment_status_display()
        representation["gender"] = instance.get_gender_display()
        return representation
