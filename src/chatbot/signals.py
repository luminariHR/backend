import os
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from core.vector_models import Documents
from core.vectorstores import VectorDBConnectionManager
from .models import ChatbotDocument
from .tasks import store_doc_to_vectorstore


connection_manager = VectorDBConnectionManager()


@receiver(post_save, sender=ChatbotDocument)
def my_model_post_save(sender, instance, **kwargs):
    store_doc_to_vectorstore.delay(instance.pk)


@receiver(post_delete, sender=ChatbotDocument)
def clean_up_document(sender, instance, **kwargs):
    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)
    document_id = str(instance.id)
    documents = Documents.objects.filter(
        metadata__contains={"document_id": document_id}
    )
    documents.delete()
