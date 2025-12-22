from django.apps import AppConfig


class ShareholderConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'shareholder'
    verbose_name = 'Shareholder Management'
    
    def ready(self):
        """Initialize signal handlers when app is ready"""
        import shareholder.signals
