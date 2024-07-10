from django.db import models
from users.models import Employee


class Approval(models.Model):
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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    file = models.FileField(upload_to="documents/", null=True, blank=True)

    def __str__(self):
        return f"{self.title} - {self.status}"
