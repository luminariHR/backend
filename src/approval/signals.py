from django.db.models.signals import post_save
from django.dispatch import receiver
from notifications.utils import send_notification
from .models import ReviewStep


@receiver(post_save, sender=ReviewStep)
def update_next_approval_step(sender, instance: ReviewStep, **kwargs):
    if instance.status == "approved":
        next_step = ReviewStep.objects.filter(
            agenda=instance.agenda, step_order=instance.step_order + 1
        ).first()
        if next_step:
            reviewer = next_step.reviewer
            next_step.status = "pending"
            next_step.save()
            message = f"{reviewer.name}님, 새로운 결재 요청 1건이 들어왔습니다."
            send_notification(reviewer.id, message, "agenda_requested")
        else:
            # 모든 결재 과정이 "approved"면 결재 "approved" 처리
            instance.agenda.status = "approved"
            instance.agenda.save()
            drafter = instance.agenda.drafter
            message = f"{drafter.name}님, 결재 1건이 승인되었습니다."
            send_notification(drafter.id, message, "agenda_reviewed")
    elif instance.status == "rejected":
        instance.agenda.status = "rejected"
        instance.agenda.save()
        drafter = instance.agenda.drafter
        message = f"{drafter.name}님, 결재 1건이 반려되었습니다."
        send_notification(drafter.id, message, "agenda_reviewed")
