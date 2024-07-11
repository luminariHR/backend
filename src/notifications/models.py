from django.db import models
from core.models import AbstractBaseModel
from users.models import Employee


class Notification(AbstractBaseModel):

    # Status
    TO_DO_ASSIGNED = "to_do_assigned"
    EVENT_CREATED = "event_created"
    APPOINTMENT_CREATED = "appointment_created"  # 인사발령
    AGENDA_REVIEWED = "agenda_reviewed"
    AGENDA_REQUESTED = "agenda_requested"

    NOTIFICATION_TYPE_CHOICES = (
        (TO_DO_ASSIGNED, "To Do Assigned"),
        (EVENT_CREATED, "Event Created"),
        (APPOINTMENT_CREATED, "Appointment Created"),
        (AGENDA_REVIEWED, "Agenda Reviewed"),
        (AGENDA_REQUESTED, "Agenda Requested"),
    )

    receiver = models.ForeignKey(Employee, on_delete=models.CASCADE)
    message = models.TextField()
    notification_type = models.CharField(
        choices=NOTIFICATION_TYPE_CHOICES, max_length=30
    )
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"[{self.notification_type}] {self.receiver.name}: {self.message}"
