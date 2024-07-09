from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
import datetime
from departments.models import Department
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
