from django.db import models
from core.models import AbstractBaseModel
from users.models import Employee


class Task(AbstractBaseModel):

    # Status
    TO_DO = "to_do"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

    STATUS_CHOICES = (
        (TO_DO, "To Do"),
        (IN_PROGRESS, "In Progress"),
        (COMPLETED, "Completed"),
    )

    # Importance
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

    PRIORITY_CHOICES = (
        (LOW, "Low"),
        (MEDIUM, "Medium"),
        (HIGH, "High"),
        (URGENT, "Urgent"),
    )

    title = models.CharField(max_length=20)
    content = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default=TO_DO)
    priority = models.CharField(max_length=6, choices=PRIORITY_CHOICES, default=LOW)
    is_deleted = models.BooleanField(default=False)  # 논리적 삭제
    order_index = models.FloatField()
    reporter = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name="created_tickets"
    )  # 티켓 생성자
    assignee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name="assigned_tickets"
    )  # 티켓 대상자

    class Meta:
        ordering = ["order_index"]

    def __str__(self):
        return self.title
