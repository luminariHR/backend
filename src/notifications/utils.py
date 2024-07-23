from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Notification


def send_notification(user_id, message, notification_type, context={}):
    notification = Notification.objects.create(
        receiver_id=user_id,
        message=message,
        notification_type=notification_type,
        context=context,
    )
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"user_{user_id}",
        {
            "type": "send_notification",
            "notification_type": notification_type,
            "message": message,
            "message_id": notification.id,
            "context": context,
        },
    )
