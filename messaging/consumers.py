from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
import json

from notifications.utils import notify

from .models import Conversation, Message


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.conversation_id = self.scope["url_route"]["kwargs"]["conversation_id"]
        self.room_group_name = f"chat_{self.conversation_id}"
        user = self.scope["user"]

        if not user.is_authenticated:
            await self.close()
            return

        is_member = await self.is_member(user, self.conversation_id)
        if not is_member:
            await self.close()
            return

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        content = data.get("message", "").strip()

        if not content:
            return

        message = await self.save_message(
            self.scope["user"], self.conversation_id, content
        )

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": content,
                "sender": self.scope["user"].username,
                "created": message.created.strftime("%b %d, %H:%M"),
            },
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def is_member(self, user, conversation_id):
        return Conversation.objects.filter(
            id=conversation_id, participants=user
        ).exists()

    @database_sync_to_async
    def save_message(self, user, conversation_id, content):
        conversation = Conversation.objects.get(id=conversation_id)
        message = Message.objects.create(
            conversation=conversation, sender=user, content=content
        )

        # Notify everyone in the conversation except whoever just sent it
        for recipient in conversation.participants.exclude(id=user.id):
            notify(recipient=recipient, actor=user, kind="message", target=conversation)

        return message
    
    
    
class NotificationConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        user = self.scope["user"]

        if not user.is_authenticated:
            await self.close()
            return

        # Each user gets their own private group — only their own
        # notifications ever get pushed into it.
        self.group_name = f"notifications_{user.id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def notify(self, event):
        # Called when something elsewhere in the app pushes to this
        # user's group — just forwards the payload to the browser.
        await self.send(text_data=json.dumps({
            "unread_count": event["unread_count"],
            "kind": event["kind"],
            "actor": event["actor"],
        }))