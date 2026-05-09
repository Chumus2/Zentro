from django.db import models
from django.conf import settings


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    bio = models.TextField(max_length=200, blank=True, null=True)
    icon = models.ImageField(upload_to="profile_icon/", blank=True, null=True)
    friends = models.ManyToManyField("self", blank=True)

    def __str__(self):
        return f"{self.user} - {self.user.name}"