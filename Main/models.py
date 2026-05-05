import random
from django.db import models
from django.conf import settings


class Chat(models.Model):
    icon = models.ImageField(upload_to="chat_icons/", blank=True, null=True)
    title = models.CharField(max_length=50, default="Chat")
    description = models.TextField(max_length=255 ,blank=True, null=True)
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="chats")
    admins = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="admin_chats")
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="created_chats")
    created_at = models.DateTimeField(auto_now_add=True)

    def set_creator(self):
        new_creator = self.participants.exclude(id=self.creator_id).order_by("?").first()

        if new_creator:
            self.creator = new_creator
            self.admins.add(new_creator)
            self.save()
        else:
            self.delete()

    def __str__(self):
        return self.title


class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_messages")
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender} - {self.text}"
    

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    icon = models.ImageField(upload_to="profile_icon/", blank=True, null=True)
    friends = models.ManyToManyField("self", blank=True)

    def __str__(self):
        return f"{self.user} - {self.user.name}"