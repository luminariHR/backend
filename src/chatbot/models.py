import uuid
from django.db import models
from users.models import Employee
from core.models import AbstractBaseModel
from .validators import validate_file_size, validate_file_type


def chatbot_document_directory_path(instance, filename):
    return f"chatbot/{instance.id}/{filename}"


class ChatbotMessage(AbstractBaseModel):
    CATEGORY_CHOICES = [
        ("onboarding_offboarding", "Onboarding / Offboarding"),
        ("company_policies", "Company Policies"),
        ("others", "Others"),
    ]

    author = models.ForeignKey(
        Employee, on_delete=models.CASCADE, default="", related_name="chatbot_messages"
    )
    question = models.TextField()
    answer = models.TextField()
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES)

    def __str__(self):
        return f"Date: {self.datetime}     Q: {self.question}    Answer: {self.answer}"


class ChatbotDocument(AbstractBaseModel):

    CATEGORY_CHOICES = [
        ("onboarding_offboarding", "Onboarding / Offboarding"),
        ("company_policies", "Company Policies"),
        ("others", "Others"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50)
    description = models.TextField(default="")
    file = models.FileField(upload_to=chatbot_document_directory_path)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES)

    def validate_file(self, file):
        validate_file_type(file)
        validate_file_size(file)
        return file
