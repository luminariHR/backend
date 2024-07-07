from django.db import models
from core.models import AbstractBaseModel
from users.models import Employee


class MentorshipRole(AbstractBaseModel):
    ROLE_CHOICES = [
        ("mentor", "Mentor"),
        ("mentee", "Mentee"),
    ]

    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name="mentorship_role"
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("employee", "role")

    def __str__(self):
        return f"{self.employee.name} - {self.role}"


class Match(AbstractBaseModel):

    mentor = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name="mentorship_matches_as_mentor"
    )
    mentee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name="mentorship_matches_as_mentee"
    )
    supervisor = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name="mentorship_matches_created"
    )
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)

    class Meta:
        unique_together = ("mentor", "mentee")

    def __str__(self):
        return f"멘토링 매칭: {self.mentor.id} -> {self.mentee.id}"


class Session(AbstractBaseModel):
    mentorship = models.ForeignKey(
        Match, related_name="sessions", on_delete=models.CASCADE
    )
    session_date = models.DateField()
    duration = models.DurationField()
    notes = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"멘토링 세션 {self.session_date} {self.mentorship.id}"
