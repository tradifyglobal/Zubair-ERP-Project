#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
sys.path.insert(0, '/var/www/tradifyerp/TradifyERP')
django.setup()

from accounting.models import Account

# Get all EQUITY accounts
equity_accounts = Account.objects.filter(account_type='EQUITY')
total_equity = equity_accounts.count()

if total_equity == 0:
    print("No EQUITY accounts found to delete.")
    sys.exit(0)

print(f"Found {total_equity} EQUITY accounts to delete")
print("\nDeleting EQUITY accounts...")

# Delete accounts
deleted_count = 0
for account in equity_accounts:
    try:
        print(f"✓ Deleted {account.account_number} - {account.name} - {account.account_type}")
        account.delete()
        deleted_count += 1
    except Exception as e:
        print(f"✗ Error deleting {account.account_number}: {str(e)}")

print(f"\n✓ Successfully deleted {deleted_count} EQUITY accounts")

# Show remaining accounts
from django.db.models import Count
remaining = Account.objects.values('account_type').annotate(count=Count('id')).order_by('account_type')
print(f"\nRemaining accounts by type:")
for item in remaining:
    print(f"  {item['account_type']}: {item['count']} accounts")

total_remaining = Account.objects.count()
print(f"\nTotal accounts remaining: {total_remaining}")
