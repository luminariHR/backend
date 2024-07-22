from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Message, ChatRoomParticipant
from users.models import Employee
from notifications.utils import send_notification


@receiver(post_save, sender=Message)
def handle_new_message(sender, instance: Message, **kwargs):
    chat_room = instance.chat_room
    participants = ChatRoomParticipant.objects.filter(
        chat_room=chat_room, left_at__isnull=True
    ).values_list("employee_id", flat=True)

    for user_id in participants:
        try:
            user = Employee.objects.get(id=user_id)
            message = f"새로운 메시지가 채팅방에 도착했습니다: {instance.content}"
            send_notification(user.id, message, "new_message")
        except Employee.DoesNotExist:
            continue
