from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ChatbotDocument
from .tasks import store_doc_to_vectorstore


@receiver(post_save, sender=ChatbotDocument)
def my_model_post_save(sender, instance, **kwargs):
    store_doc_to_vectorstore.delay(instance.pk)
