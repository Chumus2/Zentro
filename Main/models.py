from django.db import models
from Users.models import User


class Message(models.Model):
    chat = models.ForeignKey("Chat", on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages", null=True, blank=True)
    text = models.TextField()
    reply_to = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True, related_name="replies")
    if_system = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender} - {self.text}"
    

class MessageAttachment(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name="attachments")
    file = models.FileField(upload_to="messages/file/")
    attachment_type = models.CharField(max_length=20)


class Chat(models.Model):
    icon = models.ImageField(upload_to="chat_icons/", blank=True, null=True)
    title = models.CharField(max_length=50, default="Chat")
    description = models.TextField(max_length=255 ,blank=True, null=True)
    participants = models.ManyToManyField(User, related_name="chats")
    admins = models.ManyToManyField(User, related_name="admin_chats")
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="created_chats")
    pinned_messages = models.ManyToManyField(Message, blank=True, related_name="pinned_in_chat")
    created_at = models.DateTimeField(auto_now_add=True)

    def set_creator(self):
        new_creator = self.participants.exclude(id=self.creator_id).order_by("?").first()

        if new_creator:
            self.creator = new_creator
            self.admins.add(new_creator)
            self.save()
        else:
            self.delete()

    def delete_if_empty(self):
        if not self.participants.exists():
            self.delete()

    def __str__(self):
        return self.title
    

class Poll(models.Model):
    message = models.OneToOneField(Message, on_delete=models.CASCADE, related_name="poll")
    title = models.CharField(max_length=50, blank=True, null=True)
    question = models.CharField(max_length=255)
    is_closed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


class PollOption(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name="options")
    text = models.CharField(max_length=100)


class PollVote(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name="votes")
    option = models.ForeignKey(PollOption, on_delete=models.CASCADE, related_name="votes")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="poll_votes")

    class Meta:
        unique_together = ("option", "user")