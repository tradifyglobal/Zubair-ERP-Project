from django.apps import AppConfig


class MaintenanceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'maintenance'
    verbose_name = 'Site Maintenance Management'
    
    def ready(self):
        """Import signals when app is ready"""
        import maintenance.signals  # noqa
