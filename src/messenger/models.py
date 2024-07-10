from django.db import models
from users.models import Employee


class ChatRoom(models.Model):
    name = models.CharField(max_length=255)
    participants = models.ManyToManyField(
        Employee, through="ChatRoomParticipant", related_name="chat_rooms"
    )

    def __str__(self):
        return self.name


class ChatRoomParticipant(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)
    left_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("employee", "chat_room")

    def __str__(self):
        return f"{self.user.username} in {self.chat_room.name}"


class Message(models.Model):
    chat_room = models.ForeignKey(
        ChatRoom, on_delete=models.CASCADE, related_name="messages"
    )
    sender = models.ForeignKey(Employee, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}: {self.content[:50]}"
