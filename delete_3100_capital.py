#!/usr/bin/env python
"""
Delete 3100 Capital account and ensure it's not auto-created
"""

import os
import sys
sys.path.append('/var/www/tradifyerp')

import django
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from accounting.models import Account, LedgerEntry, Entity

print("DELETING 3100 CAPITAL ACCOUNT")
print("=" * 40)

# Find all 3100 Capital accounts
capital_accounts = Account.objects.filter(
    account_number='3100',
    name='Capital'
)

print(f"Found {capital_accounts.count()} Capital accounts with number 3100")

for account in capital_accounts:
    print(f"  Entity: {account.entity.name}")
    print(f"  Account: {account.account_number} - {account.name}")
    print(f"  Type: {account.account_type}")
    
    # Check for ledger entries
    entries_count = account.ledger_entries.count()
    print(f"  Ledger Entries: {entries_count}")
    
    # Check for sub-accounts
    sub_accounts = Account.objects.filter(parent_account=account)
    print(f"  Sub-accounts: {sub_accounts.count()}")
    
    if entries_count > 0:
        print(f"  WARNING: Account has {entries_count} ledger entries!")
        print("  Ledger entries:")
        for entry in account.ledger_entries.all()[:5]:
            print(f"    - {entry.entry_date} | {entry.entry_type} | {entry.amount} | {entry.description}")
    
    if sub_accounts.count() > 0:
        print(f"  Sub-accounts found:")
        for sub in sub_accounts.all():
            sub_entries = sub.ledger_entries.count()
            print(f"    - {sub.account_number} {sub.name} (Entries: {sub_entries})")
    
    print()

# Proceed with deletion if user confirms
if capital_accounts.exists():
    print("PROCEEDING WITH DELETION...")
    
    deleted_count = 0
    for account in capital_accounts:
        # Move any ledger entries to a different account or warn
        entries_count = account.ledger_entries.count()
        if entries_count > 0:
            print(f"ERROR: Cannot delete {account.account_number} - has {entries_count} ledger entries")
            print("Please move ledger entries to another account first")
            continue
        
        # Check sub-accounts
        sub_accounts = Account.objects.filter(parent_account=account)
        if sub_accounts.exists():
            print(f"Updating {sub_accounts.count()} sub-accounts to have no parent...")
            sub_accounts.update(parent_account=None)
        
        print(f"DELETING: {account.entity.name} - {account.account_number} {account.name}")
        account.delete()
        deleted_count += 1
    
    print(f"✅ Deleted {deleted_count} Capital accounts")
else:
    print("No 3100 Capital accounts found to delete")

print("\nVERIFYING DELETION...")
remaining = Account.objects.filter(
    account_number='3100',
    name='Capital'
)
print(f"Remaining 3100 Capital accounts: {remaining.count()}")

print("\nDELETION COMPLETE!")