from django.db.models.signals import post_save
from django.dispatch import receiver
from notifications.utils import send_notification
from .models import ReviewStep


@receiver(post_save, sender=ReviewStep)
def update_next_approval_step(sender, instance: ReviewStep, **kwargs):
    drafter_name = instance.agenda.drafter.name
    if instance.agenda.drafter.profile_image:
        drafter_profile_image_url = instance.agenda.drafter.profile_image.url
    else:
        drafter_profile_image_url = None
    if instance.status == "approved":
        next_step = ReviewStep.objects.filter(
            agenda=instance.agenda, step_order=instance.step_order + 1
        ).first()
        if next_step:
            reviewer = next_step.reviewer
            next_step.status = "pending"
            next_step.save()
            message = f"{drafter_name}님이 새로운 결재 1건을 요청했습니다."
            context = {
                "from": {
                    "name": drafter_name,
                    "profile_image": drafter_profile_image_url,
                },
                "path": f"/approval/details/{next_step.agenda.id}",
            }
            send_notification(reviewer.id, message, "agenda_requested", context)
        else:
            # 모든 결재 과정이 "approved"면 결재 "approved" 처리
            instance.agenda.status = "approved"
            instance.agenda.save()
            drafter = instance.agenda.drafter
            message = f"{drafter_name}님, 결재 1건이 승인되었습니다."
            context = {
                "from": {
                    "name": drafter_name,
                    "profile_image": drafter_profile_image_url,
                },
                "path": f"/approval/details/{instance.agenda.id}",
            }
            send_notification(drafter.id, message, "agenda_reviewed", context)
    elif instance.status == "rejected":
        instance.agenda.status = "rejected"
        instance.agenda.save()
        drafter = instance.agenda.drafter
        message = f"{drafter_name}님, 결재 1건이 반려되었습니다."
        context = {
            "from": {
                "name": drafter_name,
                "profile_image": drafter_profile_image_url,
            },
            "path": f"/approval/details/{instance.agenda.id}",
        }
        send_notification(drafter.id, message, "agenda_reviewed", context)
