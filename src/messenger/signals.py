from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Message, ChatRoomParticipant
from users.models import Employee
from notifications.utils import send_notification


@receiver(post_save, sender=Message)
def handle_new_message(sender, instance: Message, **kwargs):
    room_group_name = f"chat_{instance.chat_room.id}"
    channel_layer = get_channel_layer()

    async def get_group_channels():
        return await channel_layer.group_channels(room_group_name)

    async def get_all_participants():
        return ChatRoomParticipant.objects.filter(
            chat_room=instance.chat_room, left_at__isnull=True
        ).values_list("employee_id", flat=True)

    connected_channels = async_to_sync(get_group_channels)()
    all_participants = async_to_sync(get_all_participants)()

    connected_user_ids = set()
    for channel in connected_channels:
        user_id = int(channel.split("_")[-1])
        connected_user_ids.add(user_id)

    disconnected_user_ids = set(all_participants) - connected_user_ids

    for user_id in disconnected_user_ids:
        try:
            user = Employee.objects.get(id=user_id)
            message = f"새로운 메시지가 채팅방에 도착했습니다: {instance.content}"
            context = {
                "from": {
                    "name": instance.sender.name,
                },
                "path": f"/chat/{instance.chat_room.id}",
            }
            send_notification(user.id, message, "new_message", context)
        except Employee.DoesNotExist:
            continue
