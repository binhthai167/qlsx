from django.apps import AppConfig


class ProductionDataConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'production_data'

class ProductionDataConfig(AppConfig):
    name = 'production_data'

    def ready(self):
        import production_data.signals   # kích hoạt signals
