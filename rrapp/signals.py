from django.db.models.signals import pre_save, pre_delete
from django.dispatch import receiver
from .models import User, Photo
from django.core.files.storage import default_storage
from django.conf import settings
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
            old_avatar_path = old_avatar.path
            old_avatar_relative_path = os.path.relpath(
                old_avatar_path, settings.MEDIA_ROOT
            )
            if old_avatar_relative_path != DEFAULT_AVATAR_PATH:
                path = os.path.relpath(old_avatar_path, settings.MEDIA_ROOT)
                default_storage.delete(path)

@receiver(pre_delete, sender=Photo)
def delete_file_pre_delete(sender, instance, **kwargs):
    print(instance.image.path)
    if instance.image:
        default_storage.delete(instance.image.path)