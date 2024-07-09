from django.db import models
from core.models import AbstractBaseModel
from users.models import Employee


class Department(AbstractBaseModel):

    department_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=50)
    address = models.CharField(max_length=300, null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    head = models.OneToOneField(
        Employee,
        related_name="headed_department",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    parent_department = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="subdepartments",
    )

    def __str__(self):
        return f"{self.name} ({self.department_id})"
