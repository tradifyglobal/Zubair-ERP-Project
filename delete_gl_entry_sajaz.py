#!/usr/bin/env python3
"""
Delete specific GL entry for Sajaz Ahmed capital contribution
"""
import os
import django
import sys
from decimal import Decimal
from datetime import date

# Add the project directory to the Python path
sys.path.append('/var/www/tradifyerp')

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')

# Setup Django
django.setup()

# Import models
from accounting.models import LedgerEntry, CapitalContribution

print("DELETING GL ENTRY - CAPITAL CONTRIBUTION")
print("=========================================")

# Search for the GL entry
target_date = date(2025, 12, 17)
target_amount = Decimal('100.00')
target_reference = 'CAP-49'

print(f"\n1. SEARCHING FOR GL ENTRY...")
print(f"   Date: {target_date}")
print(f"   Reference: {target_reference}")
print(f"   Amount: {target_amount}")
print(f"   Description: Capital contribution from Sajaz Ahmed (CASH)")

# Find matching ledger entries
ledger_entries = LedgerEntry.objects.filter(
    entry_date=target_date,
    amount=target_amount,
    reference_number=target_reference,
    entry_type='DEBIT'
)

print(f"\nFound {ledger_entries.count()} matching GL entries")

for entry in ledger_entries:
    print(f"\n  GL Entry Details:")
    print(f"    ID: {entry.id}")
    print(f"    Date: {entry.entry_date}")
    print(f"    Reference: {entry.reference_number}")
    print(f"    Description: {entry.description}")
    print(f"    Account: {entry.account}")
    print(f"    Type: {entry.entry_type}")
    print(f"    Amount: {entry.amount}")
    print(f"    Status: {'Posted' if entry.is_posted else 'Draft'}")
    
    # Check if there's a related capital contribution
    cap_contrib = CapitalContribution.objects.filter(
        ledger_entry_id=entry.id
    ).first()
    
    if cap_contrib:
        print(f"    Related Capital Contribution: ID {cap_contrib.id}")
        print(f"      Contributor: {cap_contrib.stakeholder}")
        print(f"      Amount: {cap_contrib.amount}")
    
    print(f"\n  Deleting GL entry ID {entry.id}...")
    entry.delete()
    print(f"  ✅ GL entry deleted")

# Also search by description pattern
print(f"\n2. SEARCHING BY DESCRIPTION...")
desc_entries = LedgerEntry.objects.filter(
    entry_date=target_date,
    description__icontains="Sajaz Ahmed",
    amount=target_amount
)

print(f"Found {desc_entries.count()} entries matching description")

for entry in desc_entries:
    if entry.reference_number != target_reference:  # Skip if already deleted above
        print(f"\n  Additional GL Entry:")
        print(f"    ID: {entry.id}")
        print(f"    Reference: {entry.reference_number}")
        print(f"    Description: {entry.description}")
        print(f"    Amount: {entry.amount}")
        
        print(f"  Deleting GL entry ID {entry.id}...")
        entry.delete()
        print(f"  ✅ GL entry deleted")

# Verify deletion
print(f"\n3. VERIFICATION...")
remaining = LedgerEntry.objects.filter(
    entry_date=target_date,
    reference_number=target_reference
)

remaining_desc = LedgerEntry.objects.filter(
    entry_date=target_date,
    description__icontains="Sajaz Ahmed"
)

print(f"Remaining entries with reference CAP-49: {remaining.count()}")
print(f"Remaining entries mentioning Sajaz Ahmed: {remaining_desc.count()}")

if remaining.count() == 0 and remaining_desc.count() == 0:
    print("\n✅ SUCCESS: GL entry has been deleted!")
else:
    print("\n⚠️ Some entries may still exist")

print("\nGL entry deletion complete.")