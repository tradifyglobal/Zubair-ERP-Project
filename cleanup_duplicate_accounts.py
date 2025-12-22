#!/usr/bin/env python
import os
import sys
import django

# Set up Django to use production PostgreSQL database
os.environ['DJANGO_SETTINGS_MODULE'] = 'TradifyERP.settings'

sys.path.insert(0, '/var/www/tradifyerp')
os.chdir('/var/www/tradifyerp')
django.setup()

from accounting.models import Account, Entity
from django.db.models import Count

entity = Entity.objects.get(name='Tradify ERP Corporation')

print('=== CLEANUP DUPLICATE ACCOUNTS ===\n')

# Delete accounts with 0 ledger entries
accounts_to_check = [
    ('Accounts Receivable', '1200'),
    ('Sales Revenue', '4100'),
    ('Cash', '1000'),
]

total_deleted = 0
for name, number in accounts_to_check:
    accs = Account.objects.filter(entity=entity, account_number=number, name=name).annotate(entry_count=Count('ledger_entries'))
    for acc in accs:
        if acc.entry_count == 0:
            print(f'DELETING: {name} ({number}) with 0 entries')
            acc.delete()
            total_deleted += 1
        else:
            print(f'KEEPING: {name} ({number}) with {acc.entry_count} entries')

print(f'\nTotal deleted: {total_deleted}')
print('Cleanup complete')
