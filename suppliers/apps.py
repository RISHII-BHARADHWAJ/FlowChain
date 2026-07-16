from django.apps import AppConfig

class SuppliersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'suppliers'
    verbose_name = 'Suppliers'

    def ready(self):
        try:
            import suppliers.signals
        except ImportError:
            pass
