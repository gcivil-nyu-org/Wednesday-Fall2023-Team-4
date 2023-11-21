from django.apps import AppConfig


class RrappConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "rrapp"

    def ready(self):
        import rrapp.signals
