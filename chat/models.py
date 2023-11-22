from django.utils.translation import gettext_lazy as _
from django.db import models
from django.utils import timezone

from rrapp.models import User


class DirectMessage(models.Model):
    sender = models.ForeignKey(
        User,
        to_field="username",
        on_delete=models.CASCADE,
        related_name="message_sender",
    )
    receiver = models.ForeignKey(
        User,
        to_field="username",
        on_delete=models.CASCADE,
        related_name="message_receiver",
    )
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
    sender = models.ForeignKey(
        User,
        to_field="username",
        on_delete=models.CASCADE,
        related_name="permission_sender",
    )
    receiver = models.ForeignKey(
        User,
        to_field="username",
        on_delete=models.CASCADE,
        related_name="permission_receiver",
    )
    permission = models.CharField(
        choices=Permission.choices, default=Permission.ALLOWED
    )
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ('created_at',)
        unique_together = (("sender", "receiver"),)
