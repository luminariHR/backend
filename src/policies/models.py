from django.db import models
from core.models import AbstractBaseModel


class CompanyPolicy(AbstractBaseModel):
    leave_policy = models.CharField(
        max_length=20,
        choices=[("fiscal_year", "Fiscal Year"), ("hire_date", "Hire Date")],
        default="hire_date",
    )
    fiscal_year_start = models.DateField(null=True, blank=True)

    def __str__(self):
        return "Company Policy"


class LeavePolicy(AbstractBaseModel):
    name = models.CharField(max_length=100)
    description = models.TextField()
    default_leave_days = models.IntegerField()

    def __str__(self):
        return self.name
