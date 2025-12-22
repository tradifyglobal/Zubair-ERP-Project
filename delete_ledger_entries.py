#!/usr/bin/env python
"""
Script to delete specific ledger entries from Cash account (100001)
"""
import os
import sys
import django

# Setup Django environment
sys.path.insert(0, '/var/www/tradifyerp')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings_production')
django.setup()

from accounting.models import LedgerEntry
from django.db import transaction

# Reference numbers to delete
entries_to_delete = [
    'CASH-RECEIPT-17',
    'CASH-PAYMENT-25',
    'CASH-RECEIPT-16'
]

print("=" * 60)
print("LEDGER ENTRY DELETION SCRIPT")
print("=" * 60)

# Find the entries
entries = LedgerEntry.objects.filter(reference_number__in=entries_to_delete)

print(f"\nFound {entries.count()} ledger entries to delete:\n")

for entry in entries:
    print(f"  ID: {entry.id}")
    print(f"  Reference: {entry.reference_number}")
    print(f"  Account: {entry.account.account_number} - {entry.account.name}")
    print(f"  Type: {entry.entry_type}")
    print(f"  Amount: ₹{entry.amount}")
    print(f"  Date: {entry.entry_date}")
    print(f"  Description: {entry.description}")
    print("-" * 60)

# Confirm deletion
confirm = input(f"\nDo you want to DELETE these {entries.count()} entries? (yes/no): ")

if confirm.lower() == 'yes':
    with transaction.atomic():
        count = entries.count()
        entries.delete()
        print(f"\n✅ Successfully deleted {count} ledger entries!")
else:
    print("\n❌ Deletion cancelled.")

print("=" * 60)
