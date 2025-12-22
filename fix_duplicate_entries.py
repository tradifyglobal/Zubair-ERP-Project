#!/usr/bin/env python3

import os
import sys
import django

# Add the project directory to the Python path
sys.path.append('/var/www/tradifyerp')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from accounting.models import LedgerEntry, CapitalContribution

print("=== REMOVING DUPLICATE LEDGER ENTRIES ===")

# Find and remove duplicate entries created by capital contributions
duplicate_entries = LedgerEntry.objects.filter(
    reference_number__in=['CAP-38', 'CAP-39']
)

print(f"Found {duplicate_entries.count()} capital contribution ledger entries to remove:")

for entry in duplicate_entries:
    print(f"Entry {entry.id}: {entry.account.account_number} - {entry.entry_type} {entry.amount}")
    print(f"  Reference: {entry.reference_number}")
    print(f"  Description: {entry.description}")

# Delete the duplicate entries
if duplicate_entries.exists():
    print(f"\n🗑️ Deleting {duplicate_entries.count()} duplicate ledger entries...")
    deleted_count = duplicate_entries.delete()[0]
    print(f"✅ Deleted {deleted_count} entries")

# Update capital contributions to not auto-create ledger entries
print(f"\n🔧 Updating capital contributions to prevent auto-ledger creation...")

cap_38 = CapitalContribution.objects.filter(id=38).first()
cap_39 = CapitalContribution.objects.filter(id=39).first()

if cap_38:
    cap_38.ledger_entry = None
    cap_38.auto_created_gl_entries = False
    cap_38.save()
    print(f"✅ Updated capital contribution 38")

if cap_39:
    cap_39.ledger_entry = None  
    cap_39.auto_created_gl_entries = False
    cap_39.save()
    print(f"✅ Updated capital contribution 39")

print(f"\n=== VERIFICATION ===")
# Check cash account balance after cleanup
from accounting.models import Account
from django.db.models import Sum

cash_account = Account.objects.filter(account_number='100001').first()
if cash_account:
    debits = LedgerEntry.objects.filter(
        account=cash_account, entry_type='DEBIT'
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    credits = LedgerEntry.objects.filter(
        account=cash_account, entry_type='CREDIT'
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    balance = float(debits) - float(credits)
    print(f"Cash account balance after cleanup: {balance:,.2f}")
    
    if balance == 200000:  # Should be just the CP001 payment debit
        print("✅ Cash balance is now correct!")
    else:
        print(f"❌ Cash balance still incorrect. Expected: 200,000.00, Got: {balance:,.2f}")

print(f"\n=== REMAINING LEDGER ENTRIES ===")
entity = Entity.objects.filter(name__icontains='Testing').first()
remaining_entries = LedgerEntry.objects.filter(entity=entity).order_by('created_at')

for entry in remaining_entries:
    print(f"Entry {entry.id}: {entry.account.account_number} - {entry.entry_type} {entry.amount} (Ref: {entry.reference_number})")