from django.apps import AppConfig


class PtosConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "ptos"

    def ready(self):
        import ptos.signals
