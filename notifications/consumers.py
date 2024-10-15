import json
from channels.generic.websocket import AsyncWebsocketConsumer

class NotificationsConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_id = self.scope['user'].id
        self.group_name = f"notifications_user_{self.user_id}"
        
        await self.channel_layer.group_add(self.group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def notify_message(self, event):
        """
        Handles a new message notification event
        by sending the 'notify.message' to the client
        for further parsing and messages cache invalidation.
        """
        await self.send(text_data=json.dumps(event['message']))

    async def notify_received_friend_request(self, event):
        """
        Handles a received friend request notification
        event by sending the 'notify.receivedFriendRequest'
        to the client for further parsing and
        received friend requests cache invalidation.
        """
        await self.send(text_data=json.dumps(event['message']))

    async def notify_accepted_friend_request(self, event):
        """
        Handles an accepted friend request notification
        event by sending the 'notify.acceptedFriendRequest'
        to the client for further parsing and
        friend list cache invalidation.
        """
        await self.send(text_data=json.dumps(event['message']))

    async def notify_declined_friend_request(self, event):
        """
        Handles a declined friend request notification
        event by sending the 'notify.declinedFriendRequest'
        to the client for further parsing and
        sent friend requests cache invalidation.
        """
        await self.send(text_data=json.dumps(event['message']))

    async def notify_removed_friend(self, event):
        """
        Handles a removed friend notification event
        by sending the 'notify.removedFriend'
        to the client for further parsing and
        friend list cache invalidation.
        """
        await self.send(text_data=json.dumps(event['message']))

    async def notify_cleared_chat(self, event):
        """
        Handles a cleared chat notification event
        by sending the 'notify.clearedChat'
        to the client for further parsing and
        chat cache invalidation.
        """
        await self.send(text_data=json.dumps(event['message']))