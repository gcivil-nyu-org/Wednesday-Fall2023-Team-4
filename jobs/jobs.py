from django.conf import settings
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()


def expire_student_status():
    all_users = User.objects.all()
    current_time = timezone.now()
    for user in all_users:
        if current_time >= user.auto_expire_time:
            user.verified_student = False
            user.save()
