import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from .models import Notification


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if self.user.is_anonymous:
            await self.close()
        else:
            self.group_name = f"user_{self.user.id}"
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()

    async def disconnect(self, close_code):
        if not self.user.is_anonymous:
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    @sync_to_async
    def mark_notification_as_read(self, message_id):
        try:
            notification = Notification.objects.get(id=message_id, receiver=self.user)
            if notification:
                notification.is_read = True
                notification.save()
            return True
        except Notification.DoesNotExist:
            return False

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_id = data.get("message_id")
        if message_id:
            if await self.mark_notification_as_read(message_id):
                await self.send(
                    text_data=json.dumps(
                        {
                            "message": "알람을 읽었습니다.",
                            "message_id": message_id,
                        },
                        ensure_ascii=False,
                    )
                )

    async def send_notification(self, event):
        message = event["message"]
        await self.send(
            text_data=json.dumps(
                {
                    "message": message,
                    "message_id": event["message_id"],
                    "notification_type": event["notification_type"],
                },
                ensure_ascii=False,
            )
        )
