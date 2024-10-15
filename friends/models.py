from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class FriendList(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='friend_list'
    )
    friends = models.ManyToManyField(
        User,
        related_name='friend_lists',
        blank=True
    )

    def __str__(self):
        return self.user.email
    
    def add_frield(self, user):
        if not user in self.friends.all():
            self.friends.add(user)
        
    def remove_friend(self, friend):
        if friend in self.friends.all():
            self.friends.remove(friend)

    def unfriend(self, friend):
        """
        Removes a friend from your friend list and
        yourself from the other person's friend list.
        """
        if friend in self.friends.all():
            friends_friend_list = FriendList.objects.get(user=friend)
            self.remove_friend(friend)
            friends_friend_list.remove_friend(self.user)
            return True
        return False


class FriendRequest(models.Model):
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_friend_requests'
    )
    receiver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_friend_requests'
    )
    is_pending = models.BooleanField(default=True)
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.sender.email
    
    def accept(self):
        sender_friend_list = FriendList.objects.get(user=self.sender)
        receiver_friend_list = FriendList.objects.get(user=self.receiver)

        sender_friend_list.add_frield(self.receiver)
        receiver_friend_list.add_frield(self.sender)
        self.is_pending = False
        self.save()

    def decline(self):
        """
        Declines received friend request.
        """
        self.is_pending = False
        self.save()

    def cancel(self):
        """
        Cancels sent friend request.
        """
        self.is_pending = False
        self.save()
    
