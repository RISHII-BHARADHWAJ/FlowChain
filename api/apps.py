from django.apps import AppConfig

class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'
    verbose_name = 'Api'

    def ready(self):
        try:
            import api.signals
        except ImportError:
            pass
