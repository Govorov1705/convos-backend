from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework.generics import (
    ListAPIView,
    RetrieveAPIView
)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import serializers
from django.db.models import Q
from djoser.serializers import UserSerializer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .serializers import (
    FriendRequestListRetrieveSerializer,
    FriendRequestCreateUpdateDestroySerializer,
    FriendListRetrieveSerializer
)
from .models import FriendRequest, FriendList


User = get_user_model()


class FriendRequestCreateAPIView(APIView):
    def post(self, request):
        serializer = FriendRequestCreateUpdateDestroySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        sender = request.user
        receiver = serializer.validated_data['receiver']

        if sender == receiver:
            raise serializers.ValidationError('You cannot send friend request to yourself.')
        
        if FriendRequest.objects.filter(sender=sender, receiver=receiver, is_pending=True).exists():
            raise serializers.ValidationError('You already have an active friend request to this user.')

        if FriendRequest.objects.filter(sender=receiver, receiver=sender, is_pending=True).exists():
            raise serializers.ValidationError('This user has already sent you a friend request.')
        
        instance = serializer.save(sender=sender, is_pending=True)

        """
        Send received friend request notification
        event to the receiver of the friend request 
        """
        channel_layer = get_channel_layer()
        group = f'notifications_user_{receiver.id}'
        async_to_sync(channel_layer.group_send)(
            group, 
            {
                "type": "notify.received.friend.request",
                "message": {
                    "event": "notify.receivedFriendRequest" # different formating due to how frontend handles messages
                } 
            }
        )

        response_serializer = FriendRequestListRetrieveSerializer(instance)

        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    

class SentFriendRequestListAPIView(ListAPIView):
    serializer_class = FriendRequestListRetrieveSerializer

    def get_queryset(self):
        user = self.request.user
        return FriendRequest.objects.filter(sender=user, is_pending=True).order_by('-sent_at')
    

class ReceivedFriendRequestListAPIView(ListAPIView):
    serializer_class = FriendRequestListRetrieveSerializer

    def get_queryset(self):
        user = self.request.user
        return FriendRequest.objects.filter(receiver=user, is_pending=True).order_by('-sent_at')
    

class AcceptFriendRequestAPIView(APIView):
    def post(self, request, id):
        user = request.user
        friend_request = get_object_or_404(FriendRequest, receiver=user, id=id)
        friend_request.accept()

        """
        Send accepted friend request notification
        event to the sender of the friend request 
        """
        channel_layer = get_channel_layer()
        group = f'notifications_user_{friend_request.sender.id}'
        async_to_sync(channel_layer.group_send)(
            group, 
            {
                "type": "notify.accepted.friend.request",
                "message": {
                    "event": "notify.acceptedFriendRequest" # different formating due to how frontend handles messages
                }
            }
        )

        return Response(status=status.HTTP_200_OK)


class DeclineFriendRequestAPIView(APIView):
    def post(self, request, id):
        user = request.user
        friend_request = get_object_or_404(FriendRequest, receiver=user, id=id)
        friend_request.decline()

        """
        Send declined friend request notification
        event to the sender of the friend request 
        """
        channel_layer = get_channel_layer()
        group = f'notifications_user_{friend_request.sender.id}'
        async_to_sync(channel_layer.group_send)(
            group, 
            {
                "type": "notify.declined.friend.request",
                "message": {
                    "event": "notify.declinedFriendRequest" # different formating due to how frontend handles messages
                }
            }
        )

        return Response(status=status.HTTP_200_OK)
    

class CancelFriendRequestAPIView(APIView):
    def post(self, request, id):
        user = request.user
        friend_request = get_object_or_404(FriendRequest, sender=user, id=id)
        friend_request.cancel()
        return Response(status=status.HTTP_200_OK)


class FriendRequestRetrieveAPIView(RetrieveAPIView):
    serializer_class = FriendRequestListRetrieveSerializer

    def get_object(self):
        id = self.kwargs.get('id')
        user = self.request.user
        return get_object_or_404(FriendRequest, Q(sender=user) | Q(receiver=user), id=id)
    

class FriendListRetrieveAPIView(RetrieveAPIView):
    serializer_class = FriendListRetrieveSerializer

    def get_object(self):
        user = self.request.user
        return get_object_or_404(FriendList, user=user)
    

class FriendRemoveAPIView(APIView):
    def delete(self, request, id):
        user = request.user
        friend_list = get_object_or_404(FriendList, user=user)
        friend = get_object_or_404(User, id=id)

        result = friend_list.unfriend(friend)
        if result:
            """
            Send removed friend notification
            event to the removee.
            """
            channel_layer = get_channel_layer()
            group = f'notifications_user_{friend.id}'
            async_to_sync(channel_layer.group_send)(
                group, 
                {
                    "type": "notify.removed.friend",
                    "message": {
                        "event": "notify.removedFriend" # different formating due to how frontend handles messages
                    }
                }
            )

            return Response(status=status.HTTP_200_OK)
        return Response({"detail": "Friend not found."}, status=status.HTTP_404_NOT_FOUND)
    

class AddFriendSearchListAPIView(ListAPIView):
    serializer_class = UserSerializer

    def get_queryset(self):
        user = self.request.user
        email = self.request.query_params.get('email')

        if not email:
            return User.objects.none()
        
        friend_list = FriendList.objects.get(user=user)
        friends = friend_list.friends.all()
        pending_requests = FriendRequest.objects.filter(
            Q(sender=user) |
            Q(receiver=user),
            is_pending=True
        )

        return User.objects.filter(email__icontains=email).exclude(
            Q(id__in=friends) |
            Q(id=user.id) | 
            Q(id__in=pending_requests.values('sender')) |
            Q(id__in=pending_requests.values('receiver'))
        )
  
        