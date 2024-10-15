from rest_framework import serializers
from djoser.serializers import UserSerializer

from .models import Message, Chat


class ChatListRetrieveSerializer(serializers.ModelSerializer):
    members = UserSerializer(
        many=True,
        read_only=True
    )

    class Meta:
        model = Chat
        fields = [
            'id',
            'members',
            'created_at',
        ]   


class MessageListRetrieveSerializer(serializers.ModelSerializer):
    sender = UserSerializer(
        read_only=True
    )
    chat = ChatListRetrieveSerializer(
        read_only=True
    )

    class Meta:
        model = Message
        fields = [
            'id',
            'sender',
            'chat',
            'text',
            'sent_at',
        ]


class ChatCreateUpdateDestroySerializer(serializers.ModelSerializer):
    class Meta:
        model = Chat
        fields = [
            'id',
            'members',
            'created_at',
        ]


class ChatWithRecentMessageListSerializer(serializers.ModelSerializer):
    members = UserSerializer(
        many=True,
        read_only=True
    )
    recent_message = serializers.SerializerMethodField()

    class Meta:
        model = Chat
        fields = [
            'id',
            'members',
            'created_at',
            'recent_message'
        ]

    def get_recent_message(self, obj):
        recent_message = obj.messages.order_by('-sent_at').first()
        if recent_message:
            return MessageListRetrieveSerializer(recent_message).data
        return {}
    

class ChatWithMessagesRetrieveSerializer(serializers.ModelSerializer):
    members = UserSerializer(
        many=True,
        read_only=True
    )
    messages = MessageListRetrieveSerializer(
        many=True,
        read_only=True
    )

    class Meta:
        model = Chat
        fields = [
            'id',
            'members',
            'created_at',
            'messages'
        ]
    