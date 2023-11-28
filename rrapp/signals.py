from django.db.models.signals import pre_save, pre_delete
from django.dispatch import receiver
from .models import User, Photo
from django.core.files.storage import default_storage
import os

DEFAULT_AVATAR_PATH = 'DefaultProfile.jpg'


@receiver(pre_save, sender=User)
def delete_old_file_on_update(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_avatar = sender.objects.get(pk=instance.pk).profile_picture
        except sender.DoesNotExist:
            return
        new_avatar = instance.profile_picture
        if old_avatar and old_avatar.url != new_avatar.url:  # if avatar has changed
            old_avatar_path = old_avatar.name
            if old_avatar_path != DEFAULT_AVATAR_PATH and os.path.exists(old_avatar_path):
                default_storage.delete(old_avatar_path)


@receiver(pre_delete, sender=Photo)
def delete_file_pre_delete(sender, instance, **kwargs):
    print(instance.image.name)
    if instance.image:
        default_storage.delete(instance.image.path)
