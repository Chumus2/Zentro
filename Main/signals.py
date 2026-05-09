from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver
from .models import Chat
from Profiles.models import Profile


@receiver(pre_save, sender=Chat)
def delete_old_chat_icon_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return
    
    try:
        old_instance = Chat.objects.get(pk=instance.pk)
    except Chat.DoesNotExist:
        return
    
    old_file = old_instance.icon
    new_file = instance.icon

    if old_file and old_file != new_file:
        old_file.delete(save=False)

@receiver(post_delete, sender=Chat)
def delete_old_chat_icon_on_delete(sender, instance, **kwargs):
    if instance.icon:
        instance.icon.delete(save=False)


@receiver(pre_save, sender=Profile)
def delete_old_profile_icon_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return
    
    try:
        old_instance = Profile.objects.get(pk=instance.pk)
    except Profile.DoesNotExist:
        return
    
    old_file = old_instance.icon
    new_file = instance.icon

    if old_file and old_file != new_file:
        old_file.delete(save=False)

@receiver(post_delete, sender=Profile)
def delete_old_profile_icon_on_delete(sender, instance, **kwargs):
    if instance.icon:
        instance.icon.delete(save=False)