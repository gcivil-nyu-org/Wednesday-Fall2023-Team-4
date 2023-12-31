from django.apps import AppConfig


class RrappConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "rrapp"

    def ready(self):
        # noqa: F401
        import rrapp.signals  # noqa: F401
        from jobs import updater

        updater.start()
