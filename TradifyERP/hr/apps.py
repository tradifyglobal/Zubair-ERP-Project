"""
HR Module App Configuration
"""

from django.apps import AppConfig


class HRConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'hr'
    verbose_name = 'HR Management'
    
    def ready(self):
        """Initialize HR signals and integrations."""
        import hr.signals  # noqa
