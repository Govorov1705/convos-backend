from django.shortcuts import render, get_object_or_404
from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
    ListAPIView,
    RetrieveAPIView
)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .models import Chat, Message
from .serializers import (
    ChatListRetrieveSerializer,
    ChatCreateUpdateDestroySerializer,
    ChatWithRecentMessageListSerializer,
    ChatWithMessagesRetrieveSerializer
)


User = get_user_model()


class ChatListCreateAPIView(ListCreateAPIView):
    serializer_class = ChatListRetrieveSerializer

    def get_queryset(self):
        user = self.request.user
        return Chat.objects.filter(members=user)
    
    def create(self, request, *args, **kwargs):
        user1 = request.user
        user2_id = request.data.get('user2_id')

        if not user2_id:
            return Response(
                {'detail': 'You need to specify user2_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user2 = User.objects.get(id=user2_id)
        except User.DoesNotExist:
            return Response(
                {'detail': 'User does not exist'},
                status=status.HTTP_404_NOT_FOUND
            )

        if user1 == user2:
            return Response(
                {'detail': 'Cannot create a chat with yourself'},
                status=status.HTTP_400_BAD_REQUEST
            )

        existing_chat = Chat.objects.filter(members=user1).filter(members=user2).first()

        if existing_chat:
            serializer = self.get_serializer(existing_chat)
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

        chat = Chat.objects.create()
        chat.members.set([user1, user2])
        serializer = self.get_serializer(chat)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )


class ChatRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    def get_object(self):
        id = self.kwargs.get('id')
        user = self.request.user
        return get_object_or_404(Chat, id=id, members=user)
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ChatListRetrieveSerializer
        return ChatCreateUpdateDestroySerializer


class ChatWithRecentMessageListAPIView(ListAPIView):
    serializer_class = ChatWithRecentMessageListSerializer

    def get_queryset(self):
        user = self.request.user
        return Chat.objects.filter(
            members=user,
            messages__isnull=False
        ).distinct()


class ChatWithMessagesRetriveAPIView(RetrieveAPIView):
    serializer_class = ChatWithMessagesRetrieveSerializer

    def get_object(self):
        id = self.kwargs.get('id')
        user = self.request.user
        return get_object_or_404(Chat, id=id, members=user)
    
class ClearChatAPIView(APIView):
    def delete(self, request, id):
        user = request.user
        chat = get_object_or_404(Chat, id=id, members=user)
        Message.objects.filter(chat=chat).delete()

        other_member = chat.members.exclude(id=user.id).first()
        """
        Send cleared chat notification event
        to the other member of the chat.
        """
        channel_layer = get_channel_layer()
        group = f'notifications_user_{other_member.id}'
        async_to_sync(channel_layer.group_send)(
            group, 
            {
                "type": "notify.cleared.chat",
                "message": {
                    "event": "notify.clearedChat", # different formating due to how frontend handles messages
                    "chatId": id,
                } 
            }
        )

        return Response(status=status.HTTP_204_NO_CONTENT)
