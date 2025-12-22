#!/usr/bin/env python
"""
Clean database for customer delivery
Keeps: Test entity shareholders, chart of accounts, system configuration
Removes: Test transactions, demo data
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings_production')
sys.path.insert(0, '/var/www/tradifyerp')

django.setup()

from django.db import transaction
from accounting.models import LedgerEntry, TrialBalance
from shareholder.models import ShareholderTransaction, CapitalContribution, InvestmentReport
from apps.models import Entity

print("=" * 70)
print("DATABASE CLEANUP FOR CUSTOMER DELIVERY")
print("=" * 70)

# Get Test entity
try:
    test_entity = Entity.objects.get(name__icontains='test')
    test_entity_id = test_entity.id
    print(f"\n✓ Found Test Entity: {test_entity.name} (ID: {test_entity_id})")
except Entity.DoesNotExist:
    print("\n⚠ Test entity not found, will keep all entities")
    test_entity_id = None

print("\n--- Data to be REMOVED ---")

# Count what will be deleted
ledger_count = LedgerEntry.objects.count()
trial_balance_count = TrialBalance.objects.count()
shareholder_txn_count = ShareholderTransaction.objects.count()
capital_contrib_count = CapitalContribution.objects.count()
investment_report_count = InvestmentReport.objects.count()

print(f"  • Ledger Entries: {ledger_count}")
print(f"  • Trial Balances: {trial_balance_count}")
print(f"  • Shareholder Transactions: {shareholder_txn_count}")
print(f"  • Capital Contributions: {capital_contrib_count}")
print(f"  • Investment Reports: {investment_report_count}")

if test_entity_id:
    # Count shareholders to keep
    from shareholder.models import Shareholder
    shareholders_to_keep = Shareholder.objects.filter(entity_id=test_entity_id).count()
    print(f"\n--- Data to be KEPT ---")
    print(f"  • Test Entity Shareholders: {shareholders_to_keep}")
    print(f"  • Chart of Accounts: All accounts")
    print(f"  • Entities: All entities")
    print(f"  • User accounts: All users")

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
        print(f"✓ Deleted {deleted_ledger[0]} Ledger Entries")
        
        deleted_tb = TrialBalance.objects.all().delete()
        print(f"✓ Deleted {deleted_tb[0]} Trial Balances")
        
        deleted_sh_txn = ShareholderTransaction.objects.all().delete()
        print(f"✓ Deleted {deleted_sh_txn[0]} Shareholder Transactions")
        
        deleted_contrib = CapitalContribution.objects.all().delete()
        print(f"✓ Deleted {deleted_contrib[0]} Capital Contributions")
        
        deleted_reports = InvestmentReport.objects.all().delete()
        print(f"✓ Deleted {deleted_reports[0]} Investment Reports")
        
        print("\n✓ Cleanup completed successfully!")
        print("\nSystem is ready for customer delivery.")
        
except Exception as e:
    print(f"\n✗ Error during cleanup: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
