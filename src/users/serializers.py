from django.contrib.auth.models import Group
from django.conf import settings
from django.db import transaction
from rest_framework import serializers
from departments.models import Department
from .models import Employee, Project


class UserInviteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Employee
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(UserInviteSerializer, self).__init__(*args, **kwargs)
        # Exclude the password field
        self.fields.pop("password")

    def validate(self, data):
        filtered_data = {}
        required_fields = [
            "first_name",
            "last_name",
            "email",
            "employee_id",
            "gender",
            "employment_status",
            "job_title",
            "phone_number",
            "start_date",
        ]
        for field in required_fields:
            if field not in data:
                raise serializers.ValidationError(
                    {field: f"{field}는 필수 필드입니다."}
                )
            filtered_data[field] = data[field]
        return filtered_data


class MemberSerializer(serializers.ModelSerializer):

    class Meta:
        model = Employee
        fields = [
            "id",
            "name",
            "employee_id",
            "profile_image",
            "job_title",
            "is_ooo",
        ]


class DepartmentSerializer(serializers.ModelSerializer):
    is_head = serializers.BooleanField(read_only=True)
    members = MemberSerializer(many=True)

    class Meta:
        model = Department
        fields = ["id", "name", "members", "is_head"]

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if "is_head" in self.context:
            ret["is_head"] = self.context["is_head"]
        return ret


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ["title", "role", "duration", "description"]


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
        "is_ooo",
    ]
    is_hr_admin = serializers.BooleanField(write_only=False, required=False)
    is_department_head = serializers.SerializerMethodField(read_only=True)
    department = DepartmentSerializer()

    class Meta:
        model = Employee
        fields = [
            "id",
            "last_name",
            "first_name",
            "name",
            "email",
            "employee_id",
            "gender",
            "employment_status",
            "profile_image",
            "job_title",
            "phone_number",
            "start_date",
            "end_date",
            "is_hr_admin",
            "department",
            "is_department_head",
            "skills",
            "certifications",
            "projects",
            "location",
            "mbti",
            "hobbies",
        ]

    def get_is_department_head(self, instance):
        if instance.department:
            return instance.department.head == instance
        return False

    def is_user_hr_admin(self):
        user = self.context["request"].user
        return user.groups.filter(name=settings.HR_ADMIN_GROUP_NAME).exists()

    def validate_profile_image(self, value):
        if value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError("프로필 사진은 5MB보다 작아야 합니다.")

    @staticmethod
    def add_or_remove_hr_admin_group(is_hr_admin, user):
        if is_hr_admin is True:
            group = Group.objects.get(name=settings.HR_ADMIN_GROUP_NAME)
            group.user_set.add(user)
        elif is_hr_admin is False:
            group = Group.objects.get(name=settings.HR_ADMIN_GROUP_NAME)
            group.user_set.remove(user)

    def create(self, validated_data):
        is_hr_admin = validated_data.pop("is_hr_admin", False)
        with transaction.atomic():
            user = super().create(validated_data)
            self.add_or_remove_hr_admin_group(is_hr_admin, user)

        return user

    def update(self, instance, validated_data):
        # HR 관리자가 아닐 경우, HR 관리자 전용 필드 삭제
        if not self.is_user_hr_admin():
            for field in self.HR_ADMIN_EXCLUSIVE_FIELDS:
                validated_data.pop(field, None)
        is_hr_admin = validated_data.pop("is_hr_admin", None)
        with transaction.atomic():
            instance = super().update(instance, validated_data)
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
