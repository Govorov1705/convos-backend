from rest_framework import serializers
from djoser.serializers import UserSerializer
from django.contrib.auth import get_user_model

from .models import FriendRequest, FriendList


User = get_user_model()


class FriendRequestListRetrieveSerializer(serializers.ModelSerializer):
    sender = UserSerializer()
    receiver = UserSerializer()

    class Meta:
        model = FriendRequest
        fields = [
            'id',
            'sender',
            'receiver',
            'is_pending',
            'sent_at'
        ]


class FriendRequestCreateUpdateDestroySerializer(serializers.ModelSerializer):
    sender = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = FriendRequest
        fields = [
            'id',
            'sender',
            'receiver',
            'is_pending',
            'sent_at'
        ]

    def update(self, instance, validated_data):
        # Prevent updates to sender and receiver
        validated_data.pop('sender', None)  # Remove sender if present
        validated_data.pop('receiver', None)  # Remove receiver if present
        return super().update(instance, validated_data)
  

class FriendListRetrieveSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    friends = UserSerializer(many=True)

    class Meta:
        model = FriendList
        fields = [
            'id',
            'user',
            'friends'
        ]

