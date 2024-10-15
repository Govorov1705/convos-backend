import json
from channels.generic.websocket import AsyncWebsocketConsumer

from .utils import get_chat, create_message, serialize_message, get_other_user


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope['user']
        self.chat_id = self.scope["url_route"]["kwargs"]["chat_id"]
        self.group_name = f'chat_{self.chat_id}'
        
        chat = await get_chat(self.chat_id, user)
        if not chat:
            await self.close()

        self.chat = chat

        await self.channel_layer.group_add(self.group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):   
        text_data_json = json.loads(text_data)
        
        message = await create_message(
            user=self.scope['user'],
            chat=self.chat,
            text=text_data_json["message"]
        )

        if message:
            serialized_message = await serialize_message(message)
            """
            Send received message event to both users
            in the chat group.
            """
            await self.channel_layer.group_send(
                self.group_name, {"type": "chat.message", "message": serialized_message}
            )
            
            """         
            Send notification event about a new message
            to both user's notification groups.
            """
            user = self.scope['user']
            other_user = await get_other_user(self.chat, user)
            await self.channel_layer.group_send(
                f'notifications_user_{user.id}', {"type": "notify.message", "message": {
                    "event": "notify.message",
                    "chatId": self.chat_id
                }}
            )
            await self.channel_layer.group_send(
                f'notifications_user_{other_user.id}', {"type": "notify.message", "message": {
                    "event": "notify.message",
                    "chatId": self.chat_id
                }}
            )


    async def chat_message(self, event):
        """
        Handles received message event by sending 
        the message to both clients.
        """
        message = event["message"]

        await self.send(text_data=json.dumps({"message": message}))
