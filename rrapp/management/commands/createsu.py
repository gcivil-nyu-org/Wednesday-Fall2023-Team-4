# from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = "Creates a superuser."

    def handle(self, *args, **options):
        if not User.objects.filter(username="admin1").exists():
            User.objects.create_superuser(
                username="admin1", password="complexpassword123", email="admin1@nyu.edu"
            )
        print("Superuser has been created.")
