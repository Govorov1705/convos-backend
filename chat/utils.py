from channels.db import database_sync_to_async
from asgiref.sync import sync_to_async
from django.db.models import Q

from .models import Chat, Message
from .serializers import MessageListRetrieveSerializer


@database_sync_to_async
def get_chat(chat_id, user):
    try:
        chat = Chat.objects.get(id=chat_id, members=user)
        return chat
    except Chat.DoesNotExist:
        return None


@database_sync_to_async
def create_message(user, chat, text):
    try:
        message = Message.objects.create(
                sender=user,
                chat=chat,
                text=text
        )
        return message
    except:
        return None
    

@sync_to_async
def serialize_message(message):
    serializer = MessageListRetrieveSerializer(message)
    return serializer.data


@database_sync_to_async
def get_other_user(chat, user):
    try:
        return chat.members.filter(~Q(id=user.id)).first()
    except:
        return None