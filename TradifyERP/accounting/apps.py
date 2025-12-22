from django.apps import AppConfig


class AccountingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounting'
    verbose_name = 'Accounting'
    
    def ready(self):
        # Import signals to register them
        import accounting.signals
        from accounting.signals import register_signals
        register_signals()
        # Import theme models to ensure they're registered
        import accounting.models_theme
