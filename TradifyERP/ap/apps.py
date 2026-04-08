from django.apps import AppConfig


class ApConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ap'
    
    def ready(self):
        """Register signals for P2P GL posting"""
        import procurement.signals
