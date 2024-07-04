from django.db import models
from rest_framework.authtoken.models import Token
from users.models import Employee


class Message(models.Model):
    post = models.ForeignKey(Employee, on_delete=models.CASCADE)
    datetime = models.DateTimeField(auto_now_add=True)
    question = models.TextField()
    answer = models.TextField()

    def __str__(self):
        return f"Date: {self.datetime}     Q: {self.question}    Answer: {self.answer}"


class ChatbotDocument(models.Model):
    title = models.CharField(max_length=255)
    file_path = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


# Create your models here.
