from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Notification


def send_notification(user_id, message, notification_type):
    notification = Notification.objects.create(
        receiver_id=user_id, message=message, notification_type=notification_type
    )
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"user_{user_id}",
        {
            "type": "send_notification",
            "message": message,
            "message_id": notification.id,
        },
    )
