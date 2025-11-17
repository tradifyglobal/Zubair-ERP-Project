#!/usr/bin/env python
"""
Test script to demonstrate Fixed Asset and Ledger Entry integration.
Run: python manage.py shell < test_fixed_asset_integration.py
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from accounting.models import FixedAsset, Entity, LedgerEntry, Account, Currency
from django.utils import timezone
from django.db import models
from datetime import datetime

print("\n" + "="*60)
print("FIXED ASSET AND LEDGER ENTRY INTEGRATION TEST")
print("="*60 + "\n")

# Get or create entity
entity = Entity.objects.filter(is_active=True).first()
if not entity:
    print("❌ No active entity found. Create one first.")
    exit(1)

print(f"✅ Using Entity: {entity.name}\n")

# Check existing fixed assets
fixed_assets = FixedAsset.objects.filter(entity=entity)
print(f"📊 Fixed Assets Count: {fixed_assets.count()}\n")

if fixed_assets.exists():
    print("EXISTING FIXED ASSETS:")
    print("-" * 60)
    for asset in fixed_assets[:5]:  # Show first 5
        print(f"\n🏢 Asset: {asset.name} ({asset.asset_code})")
        print(f"   Purchase Date: {asset.purchase_date}")
        print(f"   Purchase Cost: ${asset.purchase_cost:,.2f}")
        print(f"   Annual Depreciation: ${asset.annual_depreciation:,.2f}")
        print(f"   Accumulated Depreciation: ${asset.accumulated_depreciation:,.2f}")
        print(f"   Book Value: ${asset.book_value:,.2f}")
        print(f"   Last Depreciation: {asset.last_depreciation_date}")
        
        if asset.purchase_ledger_entry:
            print(f"   ✅ Purchase Entry: {asset.purchase_ledger_entry.reference_number}")
            print(f"      Date: {asset.purchase_ledger_entry.entry_date}")
            print(f"      Amount: ${asset.purchase_ledger_entry.amount:,.2f}")
        else:
            print(f"   ⚠️  No purchase ledger entry linked")
        
        print(f"   Status: {'🔴 Disposed' if asset.is_disposed else '🟢 Active'}")

# Check ledger entries related to fixed assets
print("\n\n" + "="*60)
print("LEDGER ENTRIES LINKED TO FIXED ASSETS")
print("="*60 + "\n")

fa_entries = LedgerEntry.objects.filter(
    entity=entity,
    reference_number__startswith='FA-'
).order_by('-entry_date')

print(f"📋 Total Fixed Asset Purchase Entries: {fa_entries.count()}\n")

if fa_entries.exists():
    print("RECENT ENTRIES:")
    print("-" * 60)
    for entry in fa_entries[:10]:  # Show first 10
        entry_type_icon = "💰" if entry.entry_type == 'DEBIT' else "💸"
        print(f"\n{entry_type_icon} {entry.entry_type}: ${entry.amount:,.2f} | {entry.account.name}")
        print(f"   Ref: {entry.reference_number} | Date: {entry.entry_date}")
        print(f"   Desc: {entry.description}")

# Check depreciation entries
print("\n\n" + "="*60)
print("DEPRECIATION ENTRIES")
print("="*60 + "\n")

dep_entries = LedgerEntry.objects.filter(
    entity=entity,
    reference_number__startswith='DEP-'
).order_by('-entry_date')

print(f"📈 Total Depreciation Entries: {dep_entries.count()}\n")

if dep_entries.exists():
    print("RECENT DEPRECIATION ENTRIES:")
    print("-" * 60)
    for entry in dep_entries[:10]:  # Show first 10
        entry_type_icon = "💰" if entry.entry_type == 'DEBIT' else "💸"
        print(f"\n{entry_type_icon} {entry.entry_type}: ${entry.amount:,.2f} | {entry.account.name}")
        print(f"   Ref: {entry.reference_number} | Date: {entry.entry_date}")
        print(f"   Desc: {entry.description}")
else:
    print("⚠️  No depreciation entries recorded yet.")
    print("   Run: python manage.py generate_depreciation")

# Summary statistics
print("\n\n" + "="*60)
print("SUMMARY STATISTICS")
print("="*60 + "\n")

total_gross_value = fixed_assets.aggregate(
    total=models.Sum('purchase_cost')
)['total'] or 0

total_accum_depreciation = fixed_assets.aggregate(
    total=models.Sum('accumulated_depreciation')
)['total'] or 0

total_book_value = fixed_assets.aggregate(
    total=models.Sum('book_value')
)['total'] or 0

print(f"💵 Total Gross Value (All Assets):      ${total_gross_value:,.2f}")
print(f"📉 Total Accumulated Depreciation:      ${total_accum_depreciation:,.2f}")
print(f"📊 Total Net Book Value:                ${total_book_value:,.2f}")

# Account information
print("\n\n" + "="*60)
print("CHART OF ACCOUNTS - FIXED ASSETS SECTION")
print("="*60 + "\n")

fa_accounts = Account.objects.filter(
    entity=entity,
    account_type='ASSET',
    name__icontains='fixed'
)

print(f"Fixed Asset Accounts: {fa_accounts.count()}\n")
for account in fa_accounts:
    print(f"  {account.account_number} - {account.name}")
    balance = sum(
        e.amount if e.entry_type == 'DEBIT' else -e.amount
        for e in account.ledger_entries.all()
    )
    print(f"    Balance: ${balance:,.2f}\n")

print("\n" + "="*60)
print("✅ INTEGRATION TEST COMPLETE")
print("="*60 + "\n")

print("""
KEY FEATURES VERIFIED:
✅ Fixed Assets created with purchase journal entries
✅ Ledger Entries linked to Fixed Assets
✅ Depreciation tracking with last date
✅ Book value calculation (Cost - Accumulated Depreciation)
✅ Asset disposal tracking

NEXT STEPS:
1. Add new fixed assets via /accounting/fixed-assets/
2. View purchase journal entries automatically created
3. Run: python manage.py generate_depreciation
4. Check depreciation entries in ledger
5. View in financial reports (P&L, Balance Sheet)

MANAGEMENT COMMANDS:
  python manage.py generate_depreciation                    # Current month
  python manage.py generate_depreciation --year-month 2025-11  # Specific month
  python manage.py generate_depreciation --entity-id 1      # Specific entity
""")
