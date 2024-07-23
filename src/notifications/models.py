from django.db import models
from core.models import AbstractBaseModel
from users.models import Employee


class Notification(AbstractBaseModel):

    # Status
    TO_DO_ASSIGNED = "to_do_assigned"
    EVENT_CREATED = "event_created"
    APPOINTMENT_CREATED = "appointment_created"  # 인사발령
    AGENDA_REVIEWED = "agenda_reviewed"  # 문서 결재 리뷰
    AGENDA_REQUESTED = "agenda_requested"  # 문서 결재 요청
    PTO_REQUESTED = "pto_requested"
    PTO_REVIEWED = "pto_reviewed"
    NEW_MESSAGE = "new_message"

    NOTIFICATION_TYPE_CHOICES = (
        (TO_DO_ASSIGNED, "To Do Assigned"),
        (EVENT_CREATED, "Event Created"),
        (APPOINTMENT_CREATED, "Appointment Created"),
        (AGENDA_REVIEWED, "Agenda Reviewed"),
        (AGENDA_REQUESTED, "Agenda Requested"),
        (PTO_REQUESTED, "PTO Requested"),
        (PTO_REVIEWED, "PTO Reviewed"),
        (NEW_MESSAGE, "New Message"),
    )

    receiver = models.ForeignKey(Employee, on_delete=models.CASCADE)
    message = models.TextField()
    notification_type = models.CharField(
        choices=NOTIFICATION_TYPE_CHOICES, max_length=30
    )
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"[{self.notification_type}] {self.receiver.name}: {self.message}"
