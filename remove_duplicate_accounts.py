#!/usr/bin/env python
"""
Remove duplicate equity accounts created by auto-creation
"""

import os
import sys
sys.path.append('/var/www/tradifyerp')

import django
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from accounting.models import Account, LedgerEntry, Entity

print("REMOVING DUPLICATE EQUITY ACCOUNTS")
print("=" * 50)

# Find all duplicate Fayazuddin accounts
duplicate_accounts = Account.objects.filter(
    account_type='EQUITY',
    name__icontains='Fayazuddin'
).order_by('created_at')

print(f"Found {duplicate_accounts.count()} Fayazuddin equity accounts")

for account in duplicate_accounts:
    print(f"  {account.account_number} | {account.name} | Created: {account.created_at}")

if duplicate_accounts.count() > 1:
    print(f"\nRemoving {duplicate_accounts.count() - 1} duplicate accounts...")
    
    # Keep the first (oldest) account, delete the rest
    accounts_to_keep = duplicate_accounts.first()
    accounts_to_delete = duplicate_accounts.exclude(id=accounts_to_keep.id)
    
    print(f"KEEPING: {accounts_to_keep.account_number} | {accounts_to_keep.name}")
    
    for account in accounts_to_delete:
        # Check if account has any ledger entries
        entries_count = account.ledger_entries.count()
        print(f"DELETING: {account.account_number} | {account.name} | Entries: {entries_count}")
        
        if entries_count > 0:
            print(f"  Moving {entries_count} ledger entries to kept account...")
            # Move ledger entries to the kept account
            account.ledger_entries.update(account=accounts_to_keep)
        
        # Delete the duplicate account
        account.delete()
    
    print(f"✅ Cleanup complete! Removed {accounts_to_delete.count()} duplicate accounts")
else:
    print("No duplicates to remove")

# Show final state
print(f"\nFINAL STATE:")
remaining_accounts = Account.objects.filter(
    account_type='EQUITY',
    name__icontains='Fayazuddin'
)

for account in remaining_accounts:
    entries_count = account.ledger_entries.count()
    print(f"  {account.account_number} | {account.name} | Entries: {entries_count}")

print("\nCLEANUP COMPLETE!")