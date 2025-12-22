#!/usr/bin/env python3
"""
Delete orphaned/stale ledger entries from CAP-54
"""
import os
import django
import sys

# Add the project directory to the Python path
sys.path.append('/var/www/tradifyerp')

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')

# Setup Django
django.setup()

# Import models
from accounting.models import LedgerEntry, Entity

print("DELETING ORPHANED LEDGER ENTRIES")
print("================================")

entity = Entity.objects.get(name="Testing")

# Find the orphaned CAP-54 entries
orphaned_entries = LedgerEntry.objects.filter(
    entity=entity,
    reference_number='CAP-54',
    workflow_status='DRAFT'
)

print(f"\nFound {orphaned_entries.count()} orphaned entries:")

for entry in orphaned_entries:
    print(f"\n  Entry ID: {entry.id}")
    print(f"    Date: {entry.entry_date}")
    print(f"    Reference: {entry.reference_number}")
    print(f"    Type: {entry.entry_type}")
    print(f"    Amount: {entry.amount}")
    print(f"    Description: {entry.description}")
    print(f"    Status: {entry.workflow_status}")
    print(f"  Deleting...")
    entry.delete()
    print(f"  ✅ Deleted")

# Verify
remaining = LedgerEntry.objects.filter(
    entity=entity,
    reference_number='CAP-54'
)

print(f"\n2. VERIFICATION:")
print(f"Remaining CAP-54 entries: {remaining.count()}")

# Show updated counts
all_entries = LedgerEntry.objects.filter(entity=entity)
print(f"\nUpdated counts for {entity.name}:")
print(f"  Total: {all_entries.count()}")
print(f"  DRAFT: {all_entries.filter(workflow_status='DRAFT').count()}")
print(f"  AUTHORIZED: {all_entries.filter(workflow_status='AUTHORIZED').count()}")

if remaining.count() == 0:
    print("\n✅ All orphaned entries successfully deleted!")
    print("Page should now show: 2 total | Draft: 0 | Authorized: 2")
else:
    print("\n⚠️ Some CAP-54 entries still remain")

print("\nCleanup complete.")