from django.utils.translation import gettext_lazy as _
from django.db import models
from django.utils import timezone


class Message(models.Model):
    username = models.CharField(max_length=255)
    room = models.CharField(max_length=255)
    content = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('date_added',)


class DirectMessage(models.Model):
    sender = models.CharField(max_length=255)
    receiver = models.CharField(max_length=255)
    room = models.CharField(max_length=255)
    content = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('date_added',)


class Permission(models.TextChoices):
    REQUESTED = "requested", _("Requested")
    ALLOWED = "allowed", _("Allowed")
    BLOCKED = "blocked", _("Blocked")


class DirectMessagePermission(models.Model):
    sender = models.CharField(max_length=255)
    receiver = models.CharField(max_length=255)
    permission = models.CharField(
        choices=Permission.choices, default=Permission.ALLOWED
    )
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ('created_at',)
