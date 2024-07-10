import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import ChatRoom, Message
from users.models import Employee
from asgiref.sync import sync_to_async


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):

        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data["message"]
        employee = self.scope["user"]
        sender = await sync_to_async(Employee.objects.get)(email=employee)
        chat_room = await sync_to_async(ChatRoom.objects.get)(name=self.room_name)

        await sync_to_async(Message.objects.create)(
            chat_room=chat_room, sender=sender, content=message
        )

        await self.channel_layer.group_send(
            self.room_group_name,
            {"type": "chat_message", "message": message, "username": Employee.username},
        )

    async def chat_message(self, event):
        message = event["message"]
        username = event["username"]

        await self.send(
            text_data=json.dumps({"message": message, "username": username})
        )
