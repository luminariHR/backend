from rest_framework import serializers
from django.conf import settings
from django.db.models import Max
from .models import Task
from users.models import Employee


class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ["id", "name", "job_title"]


class TaskSerializer(serializers.ModelSerializer):
    assignee_id = serializers.IntegerField(
        write_only=True, required=False, allow_null=True
    )
    order_index = serializers.FloatField(read_only=True)
    previous_task_id = serializers.IntegerField(
        write_only=True, required=False, allow_null=True
    )
    next_task_id = serializers.IntegerField(
        write_only=True, required=False, allow_null=True
    )
    assignee = MemberSerializer(required=False)
    reporter = MemberSerializer(required=False)

    class Meta:
        model = Task
        fields = "__all__"
        read_only_fields = ["assignee", "reporter", "order_index"]

    def is_user_hr_admin(self):
        user = self.context["request"].user
        return user.groups.filter(name=settings.HR_ADMIN_GROUP_NAME).exists()

    def get_the_last_order_index(self, status):
        user = self.context["request"].user
        max_order_index = Task.objects.filter(
            status=status, assignee_id=user.id
        ).aggregate(max_order_index=Max("order_index"))["max_order_index"]
        if max_order_index is None:
            return 0
        return max_order_index + 1

    def calculate_order_index(self, task_id, is_prev):
        try:
            ref_task = Task.objects.get(id=task_id, is_deleted=False)
            if is_prev:
                query_filter = Task.objects.filter(
                    status=ref_task.status,
                    order_index__gt=ref_task.order_index,
                    is_deleted=False,
                )
            else:
                query_filter = Task.objects.filter(
                    status=ref_task.status,
                    order_index__lt=ref_task.order_index,
                    is_deleted=False,
                )
            next_task = query_filter.order_by("order_index").first()
            if next_task:
                return (
                    ref_task.status,
                    (ref_task.order_index + next_task.order_index) / 2,
                )
            else:
                return (
                    ref_task.status,
                    (
                        ref_task.order_index + 1.0
                        if is_prev
                        else ref_task.order_index - 1.0
                    ),
                )

        except Task.DoesNotExist:
            # 존재하지 않는 Task라면 아무 것도 하지 않음
            return None, None

    def create(self, validated_data):
        validated_data.pop("is_deleted", None)
        # HR 관리자면 assignee 선택 가능, 아닐 경우 본인
        request = self.context["request"]
        if self.is_user_hr_admin():
            validated_data["assignee"] = validated_data.get("assignee", request.user)
        elif "assignee" in validated_data:
            assignee_id = validated_data.pop("assignee_id")
            try:
                validated_data["assignee"] = Employee.objects.get(id=assignee_id)
            except Employee.DoesNotExist:
                raise serializers.ValidationError(
                    "존재하지 않는 유저에게 배정할 수 없습니다."
                )
        else:
            validated_data["assignee"] = request.user

        # 생성자는 무조건 본인으로 설정
        validated_data["reporter"] = request.user
        # 마지막 순서로 편입
        last_order_index = self.get_the_last_order_index(
            validated_data.get("status", Task.TO_DO)
        )
        validated_data["order_index"] = last_order_index
        return super().create(validated_data)

    def update(self, instance, validated_data):
        request = self.context["request"]
        validated_data.pop("is_deleted", None)
        # HR 관리자가 아닐 경우, assignee 수정 불가
        validated_data.pop("assignee", None)
        if not self.is_user_hr_admin():
            validated_data.pop("assignee_id", None)
        else:
            validated_data["assignee"] = validated_data.get("assignee", request.user)

        # previous_task_id가 있으면 그 task 다음으로 순번 조정
        if "previous_task_id" in validated_data and "next_task_id" in validated_data:
            raise serializers.ValidationError(
                "'previous_task_id'와 'next_task_id'는 동시에 쓸 수 없습니다."
            )
        previous_task_id = validated_data.pop("previous_task_id", None)
        if previous_task_id is not None:
            validated_data["status"], validated_data["order_index"] = (
                self.calculate_order_index(previous_task_id, True)
            )
        next_task_id = validated_data.pop("next_task_id", None)
        if next_task_id is not None:
            validated_data["status"], validated_data["order_index"] = (
                self.calculate_order_index(next_task_id, False)
            )

        # assignee 또는 status가 바뀌고 previous_task_id가 주어지지 않으면 타켓 status 마지막 순서로 편입
        assignee_changed = (
            "assignee" in validated_data
            and instance.assignee != validated_data["assignee"]
        )
        status_changed = (
            "status" in validated_data and instance.status != validated_data["status"]
        )

        if (
            (assignee_changed or status_changed)
            and not previous_task_id
            and not next_task_id
        ):
            new_status = validated_data.get("status", instance.status)
            last_order_index = self.get_the_last_order_index(new_status)
            validated_data["order_index"] = last_order_index
        return super().update(instance, validated_data)


class BoardSerializer(serializers.ModelSerializer):

    to_do = TaskSerializer(many=True)
    in_progress = TaskSerializer(many=True)
    completed = TaskSerializer(many=True)

    def to_representation(self, instance):
        ticket_list = {"to_do": [], "in_progress": [], "completed": []}
        for ticket in instance:
            if ticket.status == Task.TO_DO:
                ticket_list["to_do"].append(ticket)
            elif ticket.status == Task.IN_PROGRESS:
                ticket_list["in_progress"].append(ticket)
            elif ticket.status == Task.COMPLETED:
                ticket_list["completed"].append(ticket)
        return {
            "to_do": TaskSerializer(ticket_list["to_do"], many=True).data,
            "in_progress": TaskSerializer(ticket_list["in_progress"], many=True).data,
            "completed": TaskSerializer(ticket_list["completed"], many=True).data,
        }
