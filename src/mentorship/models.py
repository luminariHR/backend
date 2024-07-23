from django.db import models
from users.models import Employee


class Mentor(models.Model):
    employee = models.OneToOneField(
        Employee, on_delete=models.CASCADE, related_name="mentor_profile"
    )


class Mentee(models.Model):
    employee = models.OneToOneField(
        Employee, on_delete=models.CASCADE, related_name="mentee_profile"
    )


class Match(models.Model):
    mentor = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name="mentor_matches"
    )
    mentee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name="mentee_matches"
    )
    created_at = models.DateTimeField(auto_now_add=True)
