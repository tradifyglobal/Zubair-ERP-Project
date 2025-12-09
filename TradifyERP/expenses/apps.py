"""
Expense module app configuration
"""

from django.apps import AppConfig


class ExpensesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'expenses'
    verbose_name = 'Employee Expenses'

    def ready(self):
        """Import admin configuration when app is ready"""
        import expenses.admin  # noqa
