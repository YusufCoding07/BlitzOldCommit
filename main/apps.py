from django.apps import AppConfig

class MainConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main'
    verbose_name = 'Blitz Ride Hailing'

    def ready(self):
        try:
            import main.signals
        except ImportError:
            pass