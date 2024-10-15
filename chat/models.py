from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Chat(models.Model):
    members = models.ManyToManyField(
        User,
        related_name='chats'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f'{self.id}'


class Message(models.Model):
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    chat = models.ForeignKey(
        Chat,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    text = models.CharField(max_length=500)
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f'{self.sender.first_name} {self.sender.last_name}: {self.text[:30]}'
    