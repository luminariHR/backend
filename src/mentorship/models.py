from django.db import models
from users.models import Employee
from core.models import AbstractBaseModel


class Mentor(AbstractBaseModel):
    employee = models.OneToOneField(
        Employee, on_delete=models.CASCADE, related_name="mentor_profile"
    )


class Mentee(AbstractBaseModel):
    employee = models.OneToOneField(
        Employee, on_delete=models.CASCADE, related_name="mentee_profile"
    )


class Match(AbstractBaseModel):
    mentor = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name="mentor_matches"
    )
    mentee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name="mentee_matches"
    )
    start_date = models.DateField()
    end_date = models.DateField()


class Session(AbstractBaseModel):
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    note = models.TextField(null=True, blank=True)
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name="sessions")
