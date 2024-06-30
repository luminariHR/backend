from django.db import models

from core.models import AbstractBaseModel
from users.models import Employee


class Department(AbstractBaseModel):

    department_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=50)
    is_deleted = models.BooleanField(default=False)
    parent_department = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="subdepartments",
    )

    def __str__(self):
        return f"{self.name} ({self.department_id})"


class DepartmentUser(AbstractBaseModel):
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE, related_name="members"
    )
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    is_head = models.BooleanField(default=False)
    is_current = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.employee.last_name}{self.employee.first_name} ({self.department.name})"
