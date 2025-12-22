#!/usr/bin/env python
"""
Clean database for customer delivery
Removes test transactions while keeping configuration
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings_production')
sys.path.insert(0, '/var/www/tradifyerp')

django.setup()

from django.db import transaction
from accounting.models import LedgerEntry, TrialBalance
from django.contrib.sessions.models import Session

print("=" * 70)
print("DATABASE CLEANUP FOR CUSTOMER DELIVERY")
print("=" * 70)

print("\n--- Data to be REMOVED ---")

# Count what will be deleted
ledger_count = LedgerEntry.objects.count()
trial_balance_count = TrialBalance.objects.count()
session_count = Session.objects.count()

print(f"  • Ledger Entries: {ledger_count}")
print(f"  • Trial Balances: {trial_balance_count}")
print(f"  • User Sessions: {session_count}")

print(f"\n--- Data to be KEPT ---")
print(f"  • Chart of Accounts: All accounts")
print(f"  • Entities: All entities")  
print(f"  • Users: All user accounts")
print(f"  • Shareholders: All shareholders")
print(f"  • System Configuration: All settings")

print("\n" + "=" * 70)
confirm = input("Proceed with cleanup? (type 'YES' to confirm): ")

if confirm != 'YES':
    print("Cleanup cancelled.")
    sys.exit(0)

print("\nStarting cleanup...")

try:
    with transaction.atomic():
        # Delete transactional data
        deleted_ledger = LedgerEntry.objects.all().delete()
        print(f"✓ Deleted {deleted_ledger[0]} Ledger Entries and related records")
        
        deleted_tb = TrialBalance.objects.all().delete()
        print(f"✓ Deleted {deleted_tb[0]} Trial Balances")
        
        deleted_sessions = Session.objects.all().delete()
        print(f"✓ Deleted {deleted_sessions[0]} User Sessions")
        
        print("\n" + "=" * 70)
        print("✓ CLEANUP COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        print("\nSystem is ready for customer delivery.")
        print("Configuration, users, and master data preserved.")
        
except Exception as e:
    print(f"\n✗ Error during cleanup: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
