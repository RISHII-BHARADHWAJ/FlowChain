from django.apps import AppConfig

class WarehousesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'warehouses'
    verbose_name = 'Warehouses'

    def ready(self):
        try:
            import warehouses.signals
        except ImportError:
            pass
