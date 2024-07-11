from django.db import models
from django.utils import timezone
from users.models import Employee
from departments.models import Department
from core.models import AbstractBaseModel


class Approval(AbstractBaseModel):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]
    requester = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name="requests"
    )
    approver = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name="approvals"
    )
    title = models.CharField(max_length=255)
    document_content = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    # file = models.FileField(upload_to="documents/", null=True, blank=True)

    def __str__(self):
        return f"{self.title} - {self.status}"


class Agenda(AbstractBaseModel):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]
    title = models.CharField(max_length=255)
    content = models.TextField()
    drafter = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name="agendas"
    )
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE, related_name="agendas"
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")

    def get_review_step_for_reviewer(self, reviewer_id):
        return self.review_steps.filter(reviewer_id=reviewer_id).first()


class Reference(AbstractBaseModel):
    referrer = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name="references"
    )
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE, related_name="references"
    )
    agenda = models.ForeignKey(
        "Agenda", on_delete=models.CASCADE, related_name="references"
    )


class ReviewStep(AbstractBaseModel):
    STATUS_CHOICES = [
        ("standby", "Standby"),
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="standby")
    step_order = models.IntegerField(default=0)
    reviewer = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name="reviews"
    )
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE, related_name="reviewed_agendas"
    )
    agenda = models.ForeignKey(
        "Agenda", on_delete=models.CASCADE, related_name="review_steps"
    )

    class Meta:
        unique_together = (("agenda", "step_order"),)
        ordering = ["step_order"]
