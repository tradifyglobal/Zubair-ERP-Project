#!/usr/bin/env python
"""
Script to delete accounts starting with 3100-01
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from accounting.models import Account

# Find accounts starting with 3100-01
accounts_to_delete = Account.objects.filter(account_number__startswith='3100-01')

print(f"Found {accounts_to_delete.count()} accounts starting with '3100-01':")
for account in accounts_to_delete:
    print(f"  - {account.account_number} - {account.name}")

if accounts_to_delete.count() == 0:
    print("No accounts found to delete.")
    exit(0)

# Confirm deletion
print(f"\nDeleting {accounts_to_delete.count()} accounts...")
deleted_count = 0

for account in accounts_to_delete:
    try:
        account_number = account.account_number
        account_name = account.name
        account.delete()
        deleted_count += 1
        print(f"  ✓ Deleted {account_number} - {account_name}")
    except Exception as e:
        print(f"  ✗ Error deleting {account.account_number}: {str(e)}")

print(f"\n✓ Successfully deleted {deleted_count} accounts")
print(f"Total accounts remaining: {Account.objects.count()}")

# Show remaining accounts by type
print("\nRemaining accounts by type:")
from django.db.models import Count
accounts_by_type = Account.objects.values('account_type').annotate(count=Count('id')).order_by('account_type')
for item in accounts_by_type:
    print(f"  {item['account_type']}: {item['count']} accounts")
