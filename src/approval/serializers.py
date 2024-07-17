import uuid
from rest_framework import serializers
from users.models import Employee
from departments.models import Department
from notifications.utils import send_notification
from django.db import transaction
from .models import Approval, Agenda, ReviewStep, Reference
from .validators import validate_file_size


class ApprovalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Approval
        fields = "__all__"
        read_only_fields = ["requester", "status", "created_at", "updated_at"]

    def create(self, validated_data):
        validated_data["requester"] = self.context["request"].user
        return super().create(validated_data)


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ["id", "name"]


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ["id", "name"]


class ReviewStepSerializer(serializers.ModelSerializer):
    reviewer = EmployeeSerializer(read_only=True)
    department = DepartmentSerializer(read_only=True)

    class Meta:
        model = ReviewStep
        fields = [
            "id",
            "created_at",
            "updated_at",
            "status",
            "reviewer",
            "department",
        ]


class ReferenceSerializer(serializers.ModelSerializer):
    referrer = EmployeeSerializer(read_only=True)
    department = DepartmentSerializer(read_only=True)

    class Meta:
        model = ReviewStep
        fields = ["id", "created_at", "updated_at", "referrer", "department"]


class AgendaSerializer(serializers.ModelSerializer):
    drafter = EmployeeSerializer(read_only=True)
    department = DepartmentSerializer(read_only=True)
    review_steps = ReviewStepSerializer(read_only=True, many=True)
    references = ReferenceSerializer(read_only=True, many=True)

    class Meta:
        model = Agenda
        fields = [
            "id",
            "created_at",
            "updated_at",
            "title",
            "content",
            "drafter",
            "department",
            "status",
            "review_steps",
            "references",
            "file",
        ]

    def get_file_path(self, obj):
        request = self.context.get("request")
        if obj.file:
            return request.build_absolute_uri(obj.file.url)


class AgendaReviewRequestCreateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    content = serializers.CharField()
    file = serializers.FileField(allow_null=True, required=False)
    referrer_ids = serializers.ListField(
        child=serializers.IntegerField(), default=[], allow_null=True
    )
    reviewer_ids = serializers.ListField(child=serializers.IntegerField())

    def validate_referrer_ids(self, value):
        if not all(
            Employee.objects.filter(id=referrer_id).exists() for referrer_id in value
        ):
            raise serializers.ValidationError(
                "존재하지 않는 참조인이 포함되어 있습니다."
            )
        return value

    def validate_reviewer_ids(self, value):
        if not all(
            Employee.objects.filter(id=reviewer_id).exists() for reviewer_id in value
        ):
            raise serializers.ValidationError(
                "존재하지 않는 결재권자가 포함되어 있습니다."
            )
        return value

    @transaction.atomic
    def create(self, validated_data):
        referrer_ids = validated_data.pop("referrer_ids")
        reviewer_ids = validated_data.pop("reviewer_ids")
        file = validated_data.pop("file", None)
        request = self.context["request"]
        drafter = request.user

        # 생성된 결재 요청
        agenda = Agenda.objects.create(
            id=str(uuid.uuid4()),
            title=validated_data["title"],
            content=validated_data["content"],
            drafter=drafter,
            department=drafter.department,
            status="pending",
            file=file,
        )

        # 결재 단계 생성
        for order, reviewer_id in enumerate(reviewer_ids):
            reviewer = Employee.objects.get(id=reviewer_id)
            ReviewStep.objects.create(
                agenda=agenda,
                reviewer_id=reviewer_id,
                department=reviewer.department,
                step_order=order,
                status="pending" if order == 0 else "standby",
            )
            if order == 0:
                message = f"{reviewer.name}님, 새로운 결재 요청 1건이 들어왔습니다."
                send_notification(reviewer.id, message, "agenda_requested")

        # 참조 관계 생성
        for referrer_id in referrer_ids:
            referrer = Employee.objects.get(id=referrer_id)
            Reference.objects.create(
                agenda=agenda,
                referrer_id=referrer_id,
                department=referrer.department,
            )

        return agenda


class AgendaReviewSerializer(serializers.Serializer):

    STATUS_CHOICES = [
        ("standby", "Standby"),
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]
    status = serializers.CharField(max_length=10)

    def validate_status(self, value):
        if value not in ["approved", "rejected"]:
            raise serializers.ValidationError("결재는 승인 또는 반려만 가능합니다.")
        return value

    def update(self, instance: Agenda, validated_data):
        status = validated_data.pop("status", None)
        request = self.context["request"]
        user = request.user
        review_step = instance.get_review_step_for_reviewer(user.id)
        if not review_step:
            raise serializers.ValidationError("처리할 수 없는 결재입니다.")
        if review_step.status != "pending":
            raise serializers.ValidationError("처리할 수 없는 결재입니다.")
        review_step.status = status
        review_step.save()
        return instance


class OCRSerializer(serializers.Serializer):
    image = serializers.ImageField(validators=[validate_file_size])
