#!/usr/bin/env python
"""
Script to check accounts in the database
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from accounting.models import Account

print("Total accounts in database:", Account.objects.count())
print("\nAccounts by type:")

# Group by account type
from django.db.models import Count
accounts_by_type = Account.objects.values('account_type').annotate(count=Count('id')).order_by('account_type')

for item in accounts_by_type:
    print(f"  {item['account_type']}: {item['count']} accounts")

print("\nAll accounts:")
for account in Account.objects.all().order_by('account_number'):
    print(f"  {account.account_number} - {account.name} ({account.account_type})")

print(f"\nTotal: {Account.objects.count()} accounts")
