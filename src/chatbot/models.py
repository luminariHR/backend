from django.db import models
from rest_framework.authtoken.models import Token
from users.models import Employee


class Message(models.Model):
    post = models.ForeignKey(Employee, on_delete=models.CASCADE, default="")
    datetime = models.DateTimeField(auto_now_add=True)
    question = models.TextField()
    answer = models.TextField()

    def __str__(self):
        return f"Date: {self.datetime}     Q: {self.question}    Answer: {self.answer}"
