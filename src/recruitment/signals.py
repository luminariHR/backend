from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import EssayAnswer
from .tasks import summarize


# @receiver(post_save, sender=EssayAnswer)
# def run_ai_model(sender, instance, **kwargs):
#     summarize.delay(
#         instance.job_posting.id, instance.applicant_name, instance.applicant_email
#     )
