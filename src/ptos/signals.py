from django.db.models.signals import post_save
from django.dispatch import receiver
from notifications.utils import send_notification
from .models import PTO


@receiver(post_save, sender=PTO)
def send_pto_notification(sender, instance: PTO, created, **kwargs):
    authorizer = instance.authorizer
    employee = instance.employee
    if created and instance.status == "pending":
        message = (
            f"{authorizer.name}님, {employee.name}님의 휴가 요청 1건이 들어왔습니다."
        )
        send_notification(
            authorizer.id,
            message,
            "pto_requested",
            {"pto_id": instance.id},
        )
    elif instance.status == "approved":
        message = f"{employee.name}님, 휴가 요청 1건이 승인되었습니다."
        send_notification(employee.id, message, "pto_reviewed", {"pto_id": instance.id})
    elif instance.status == "rejected":
        message = f"{employee.name}님, 휴가 요청 1건이 반려되었습니다."
        send_notification(employee.id, message, "pto_reviewed", {"pto_id": instance.id})
