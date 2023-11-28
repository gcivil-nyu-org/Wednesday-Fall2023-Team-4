from django.db.models import Q
from .models import DirectMessagePermission, Permission


def get_pending_connections_count(username):
    try:
        pending_connections_count = DirectMessagePermission.objects.filter(
            Q(receiver__exact=username) & Q(permission__exact=Permission.REQUESTED)
        ).count()
    except DirectMessagePermission.DoesNotExist:
        pending_connections_count = 0

    return pending_connections_count
