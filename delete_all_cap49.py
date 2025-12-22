#!/usr/bin/env python3
"""
Delete all GL entries related to Sajaz Ahmed CAP-49
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

print("DELETING ALL GL ENTRIES - CAP-49")
print("================================")

target_date = date(2025, 12, 17)
target_reference = 'CAP-49'

print(f"\n1. FINDING ALL ENTRIES WITH REFERENCE CAP-49...")

# Find ALL entries with this reference
all_entries = LedgerEntry.objects.filter(
    entry_date=target_date,
    reference_number=target_reference
)

print(f"Found {all_entries.count()} GL entries with reference CAP-49")

for entry in all_entries:
    print(f"\n  Entry ID: {entry.id}")
    print(f"    Type: {entry.entry_type}")
    print(f"    Amount: {entry.amount}")
    print(f"    Account: {entry.account}")
    print(f"    Description: {entry.description}")
    print(f"  Deleting...")
    entry.delete()
    print(f"  ✅ Deleted")

# Verify
remaining = LedgerEntry.objects.filter(
    entry_date=target_date,
    reference_number=target_reference
)

print(f"\n2. VERIFICATION...")
print(f"Remaining entries with CAP-49: {remaining.count()}")

if remaining.count() == 0:
    print("✅ All CAP-49 GL entries successfully deleted!")
else:
    print("⚠️ Some entries still remain:")
    for entry in remaining:
        print(f"  - ID {entry.id}: {entry.entry_type} {entry.amount}")

print("\nDeletion complete.")