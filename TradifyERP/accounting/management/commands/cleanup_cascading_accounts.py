"""
Management command to clean up cascading duplicate accounts
Run: python manage.py cleanup_cascading_accounts
"""

from django.core.management.base import BaseCommand
from django.db import connection
from accounting.models import Account


class Command(BaseCommand):
    help = 'Remove cascading duplicate accounts to improve performance'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('═'*70))
        self.stdout.write(self.style.SUCCESS('CLEANING UP CASCADING ACCOUNTS'))
        self.stdout.write(self.style.SUCCESS('═'*70))
        
        # Count before
        before = Account.objects.count()
        self.stdout.write(f'\nBefore: {before} accounts')
        
        # Delete cascading accounts (those with multiple dashes like 3000-01-01-01)
        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM accounting_account WHERE account_number LIKE %s",
                ['%-%-%']
            )
            deleted = cursor.rowcount
        
        # Count after
        after = Account.objects.count()
        
        self.stdout.write(f'Deleted: {deleted} cascading accounts')
        self.stdout.write(f'After: {after} accounts')
        self.stdout.write(f'\nReduction: {before - after} accounts')
        
        # Show breakdown
        self.stdout.write('\nAccounts by entity:')
        from accounting.models import Entity
        for entity in Entity.objects.all():
            count = Account.objects.filter(entity=entity).count()
            self.stdout.write(f'  {entity.code}: {count}')
        
        self.stdout.write(self.style.SUCCESS('\n✅ Cleanup complete - ERP performance should improve!'))
