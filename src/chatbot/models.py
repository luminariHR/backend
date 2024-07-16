import uuid
from django.db import models
from users.models import Employee
from core.models import AbstractBaseModel


def chatbot_document_directory_path(instance, filename):
    return f"chatbot/{instance.id}/{filename}"


class Message(AbstractBaseModel):
    post = models.ForeignKey(
        Employee, on_delete=models.CASCADE, default="", related_name="chatbot_posts"
    )
    question = models.TextField()
    answer = models.TextField()

    def __str__(self):
        return f"Date: {self.datetime}     Q: {self.question}    Answer: {self.answer}"


class ChatbotDocument(AbstractBaseModel):

    CATEGORY_CHOICES = [
        ("onboarding_offboarding", "Onboarding / Offboarding"),
        ("company_policies", "Company Policies"),
        ("others", "Others"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file = models.FileField(upload_to=chatbot_document_directory_path)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES)
