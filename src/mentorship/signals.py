import json
import datetime
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from core.vector_models import MentorshipDocuments
from users.models import Employee
from .models import Mentor, Mentee
from .tasks import add_profiles_to_vector_store


def delete_documents_associated_with_employee_id(employee_id):
    documents = MentorshipDocuments.objects.filter(
        metadata__contains={"employee_id": employee_id}
    )
    documents.delete()


@receiver(post_save, sender=Mentee)
@receiver(post_save, sender=Mentor)
def process_profile(sender, instance, created, **kwargs):
    if created:
        model_class = type(instance)
        if model_class == Mentor:
            role = "멘토"
        else:
            role = "멘티"
        content = json.dumps(
            {
                "ID": instance.employee.id,
                "이름": instance.employee.name,
                "역할": role,
                "직책": instance.employee.job_title,
                "거주지역": instance.employee.location,
                "MBTI": instance.employee.mbti,
                "취미/관심사": ", ".join(instance.employee.hobbies),
                "근속연수": datetime.datetime.now().year
                - instance.employee.start_date.year,
            },
            ensure_ascii=False,
        )
        add_profiles_to_vector_store.delay(content, instance.employee.id)


@receiver(post_save, sender=Employee)
def process_profile_update(sender, instance, created, **kwargs):
    if not created:
        employee_id = instance.id
        delete_documents_associated_with_employee_id(employee_id)
        if instance.mentor_profile:
            content = json.dumps(
                {
                    "ID": instance.employee.id,
                    "이름": instance.employee.name,
                    "역할": "멘토",
                    "직책": instance.employee.job_title,
                    "거주지역": instance.employee.location,
                    "MBTI": instance.employee.mbti,
                    "취미/관심사": ", ".join(instance.employee.hobbies),
                    "근속연수": datetime.datetime.now().year
                    - instance.employee.start_date.year,
                },
                ensure_ascii=False,
            )
            add_profiles_to_vector_store.delay(content, instance.employee.id)
        elif instance.mentee_profile:
            content = json.dumps(
                {
                    "ID": instance.employee.id,
                    "이름": instance.employee.name,
                    "역할": "멘티",
                    "직책": instance.employee.job_title,
                    "거주지역": instance.employee.location,
                    "MBTI": instance.employee.mbti,
                    "취미/관심사": ", ".join(instance.employee.hobbies),
                    "근속연수": datetime.datetime.now().year
                    - instance.employee.start_date.year,
                },
                ensure_ascii=False,
            )
            add_profiles_to_vector_store.delay(content, instance.employee.id)


@receiver(post_delete, sender=Mentee)
@receiver(post_delete, sender=Mentor)
def clean_up_profile(sender, instance, **kwargs):
    employee_id = instance.employee.id
    delete_documents_associated_with_employee_id(employee_id)
