#!/usr/bin/env python
"""
Fast cleanup script to remove cascading duplicate accounts from database.
Run on the application server where Django is configured.
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings_production')
django.setup()

from accounting.models import Account
from django.db import connection

print('='*70)
print('BULK DELETE CASCADING ACCOUNTS')
print('='*70)

# Count before
before = Account.objects.count()
print(f'\nTotal accounts before: {before}')

# Use raw SQL for fastest deletion
with connection.cursor() as cursor:
    # Delete cascading accounts (account numbers with multiple dashes like 3000-01-01-01)
    cursor.execute("""
        DELETE FROM accounting_account 
        WHERE account_number LIKE '%-%-%'
    """)
    deleted = cursor.rowcount
    print(f'Deleted {deleted} cascading accounts')

# Verify
after = Account.objects.count()
print(f'Total accounts after: {after}')
print(f'Reduction: {before - after} accounts removed')

# Show breakdown by entity
print('\nAccounts by entity:')
for entity in ['INT-001', 'MAIN', 'Test']:
    from accounting.models import Entity
    try:
        e = Entity.objects.get(code=entity)
        c = Account.objects.filter(entity=e).count()
        print(f'  {entity}: {c}')
    except:
        pass

print('\n✅ Cleanup complete - ERP should be faster now!')
