from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Message, ChatRoomParticipant
from users.models import Employee
from notifications.models import Notification
from notifications.utils import send_notification


@receiver(post_save, sender=Message)
def handle_new_message(sender, instance: Message, **kwargs):
    chat_room = instance.chat_room
    sender_id = instance.sender.id
    participants = ChatRoomParticipant.objects.filter(
        chat_room=chat_room, left_at__isnull=True
    ).values_list("employee_id", flat=True)

    participants_to_notify = [
        user_id for user_id in participants if user_id != sender_id
    ]
    message = f"새로운 메시지가 채팅방에 도착했습니다: {chat_room.name}"

    for user_id in participants_to_notify:
        try:
            unread_notification = Notification.objects.filter(
                receiver_id=user_id,
                message=message,
                notification_type="new_message",
                is_read=False,
            ).first()

            if not unread_notification:
                sender_name = instance.sender.name
                if instance.sender.profile_image:
                    sender_profile_image_url = instance.sender.profile_image.url
                else:
                    sender_profile_image_url = None
                content = {
                    "from": {
                        "name": sender_name,
                        "profile_image": sender_profile_image_url,
                    },
                    "path": "/chatting",
                }
                send_notification(user_id, message, "new_message", content)
        except Notification.DoesNotExist:
            continue
