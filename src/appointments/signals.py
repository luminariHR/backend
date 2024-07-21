import datetime
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from departments.models import Department
from notifications.utils import send_notification
from .models import Appointment


@receiver(post_save, sender=Appointment)
def apply_appointment(sender, instance, **kwargs):
    # TODO: 현재는 당일 인사 발령만 처리 가능
    with transaction.atomic():
        if instance.effective_date == datetime.date.today():
            employee = instance.employee
            employee.job_title = instance.new_job_title
            employee.department = Department.objects.get(id=instance.new_department_id)
            employee.save()
            employee.refresh_from_db()
            if instance.is_department_head:
                employee.department.head = employee
            else:
                employee.department.head = None
            employee.department.save()
            # 인사 발령 노티
            message = f"{instance.effective_date} 부로 팀/직책이 변경 되었습니다!"

            context = {
                "from": {
                    "name": employee.name,
                    "profile_image": employee.profile_image.url,
                },
                "path": "/myprofile",
            }
            send_notification(employee.id, message, "appointment_created", context)
