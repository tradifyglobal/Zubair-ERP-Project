#!/usr/bin/env python3
"""
Check all ledger entries in Testing entity
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

print("CHECKING ALL LEDGER ENTRIES")
print("===========================")

# Get Testing entity
entity = Entity.objects.get(name="Testing")
print(f"Entity: {entity.name} (ID: {entity.id})")

# Get all ledger entries
all_entries = LedgerEntry.objects.filter(entity=entity).order_by('-entry_date', '-id')

print(f"\nTotal Ledger Entries: {all_entries.count()}")

print(f"\nByWorkflow Status:")
print(f"  DRAFT: {all_entries.filter(workflow_status='DRAFT').count()}")
print(f"  PENDING_APPROVAL: {all_entries.filter(workflow_status='PENDING_APPROVAL').count()}")
print(f"  APPROVED: {all_entries.filter(workflow_status='APPROVED').count()}")
print(f"  AUTHORIZED: {all_entries.filter(workflow_status='AUTHORIZED').count()}")
print(f"  REJECTED: {all_entries.filter(workflow_status='REJECTED').count()}")

print(f"\n1. ALL LEDGER ENTRIES DETAILED:")
for i, entry in enumerate(all_entries, 1):
    print(f"\n{i}. ID: {entry.id}")
    print(f"   Date: {entry.entry_date}")
    print(f"   Account: {entry.account.account_number} - {entry.account.name}")
    print(f"   Type: {entry.entry_type}")
    print(f"   Amount: {entry.amount}")
    print(f"   Description: {entry.description}")
    print(f"   Reference: {entry.reference_number}")
    print(f"   Workflow Status: {entry.workflow_status}")
    print(f"   Is Posted: {entry.is_posted}")

# Check for orphaned/stale entries
print(f"\n2. CHECK FOR STALE ENTRIES:")
stale_entries = all_entries.filter(workflow_status='DRAFT')
print(f"Draft entries: {stale_entries.count()}")
for entry in stale_entries:
    print(f"  - ID {entry.id}: {entry.description} - {entry.reference_number}")

# Show the default view filter
print(f"\n3. VIEW FILTER ANALYSIS:")
print(f"Default filter (APPROVED,AUTHORIZED):")
filtered = all_entries.filter(workflow_status__in=['APPROVED', 'AUTHORIZED'])
print(f"  Count: {filtered.count()}")
for entry in filtered:
    print(f"  - ID {entry.id}: {entry.workflow_status} - {entry.entry_type} {entry.amount}")

print(f"\nThis explains why page shows '4 total' but only displays 2 AUTHORIZED entries")