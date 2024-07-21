from django.db.models.signals import post_save
from django.dispatch import receiver
from notifications.utils import send_notification
from .models import PTO


@receiver(post_save, sender=PTO)
def send_pto_notification(sender, instance: PTO, created, **kwargs):
    authorizer = instance.authorizer
    employee = instance.employee
    employee_name = employee.name
    if employee.profile_image:
        employee_profile_image_url = employee.profile_image.url
    else:
        employee_profile_image_url = None
    if created and instance.status == "pending":
        message = f"{employee_name}님의 휴가 요청 1건이 들어왔습니다."
        context = {
            "from": {
                "name": employee_name,
                "profile_image": employee_profile_image_url,
            },
            "path": f"/vacation/details/{str(instance.id)}",
        }
        send_notification(authorizer.id, message, "pto_requested", context)
    elif instance.status == "approved":
        message = f"{employee_name}님의 휴가 요청 1건이 승인되었습니다."
        context = {
            "from": {
                "name": employee_name,
                "profile_image": employee_profile_image_url,
            },
            "path": f"/vacation/details/{str(instance.id)}",
        }
        send_notification(employee.id, message, "pto_reviewed", context)
    elif instance.status == "rejected":
        message = f"{employee_name}님의 휴가 요청 1건이 반려되었습니다."
        context = {
            "from": {
                "name": employee_name,
                "profile_image": employee_profile_image_url,
            },
            "path": f"/vacation/details/{str(instance.id)}",
        }
        send_notification(employee.id, message, "pto_reviewed", context)
