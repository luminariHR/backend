from django.db import models
from core.models import AbstractBaseModel
from departments.models import Department
from users.models import Employee
import datetime


class Appointment(AbstractBaseModel):
    employee = models.ForeignKey(
        Employee, related_name="appointments", on_delete=models.PROTECT
    )
    new_job_title = models.CharField(max_length=100)
    new_department = models.ForeignKey(
        Department, related_name="appointments", on_delete=models.PROTECT
    )
    is_department_head = models.BooleanField(default=False)
    effective_date = models.DateField(default=datetime.date.today)
    note = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Appointment<{self.employee_id} - {self.new_department} - {self.new_job_title}>"
