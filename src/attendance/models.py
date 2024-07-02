from django.db import models
import datetime
from users.models import Employee


class Attendance(models.Model):

    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name="attendance"
    )
    date = models.DateField(default=datetime.date.today)
    clock_in = models.DateTimeField(blank=True, null=True)
    clock_out = models.DateTimeField(blank=True, null=True)
    is_late = models.BooleanField(default=False)
    is_early_leave = models.BooleanField(default=False)
    is_excused = models.BooleanField(default=False)
    overtime = models.FloatField(default=0.0)
    clock_in_note = models.TextField(blank=True, null=True)
    clock_out_note = models.TextField(blank=True, null=True)
    hr_note = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ("employee", "date")
        ordering = ["date"]
        get_latest_by = "date"

    def __str__(self):
        return f"{self.employee.employee_id} - {self.date}"
