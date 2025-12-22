#!/usr/bin/env python3
"""
Investigate the cash receipt count discrepancy
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
from accounting.models import CashReceiptLine, Entity

print("INVESTIGATING CASH RECEIPT COUNT DISCREPANCY")
print("===========================================")

# Get Testing entity
entity = Entity.objects.get(name="Testing")
print(f"Entity: {entity.name} (ID: {entity.id})")

# Get all cash receipts for this entity
all_receipts = CashReceiptLine.objects.filter(entity=entity).order_by('-date', '-id')

print(f"\n1. ALL CASH RECEIPTS IN TESTING ENTITY:")
print(f"Total count: {all_receipts.count()}")

print(f"\nBreakdown by status field:")
print(f"  DRAFT: {all_receipts.filter(status='DRAFT').count()}")
print(f"  POSTED: {all_receipts.filter(status='POSTED').count()}")

print(f"\nBreakdown by workflow_status field:")
print(f"  DRAFT: {all_receipts.filter(workflow_status='DRAFT').count()}")
print(f"  PENDING_APPROVAL: {all_receipts.filter(workflow_status='PENDING_APPROVAL').count()}")
print(f"  APPROVED: {all_receipts.filter(workflow_status='APPROVED').count()}")
print(f"  AUTHORIZED: {all_receipts.filter(workflow_status='AUTHORIZED').count()}")
print(f"  REJECTED: {all_receipts.filter(workflow_status='REJECTED').count()}")

print(f"\n2. DETAILED RECEIPT LIST:")
for receipt in all_receipts:
    print(f"\nID: {receipt.id}")
    print(f"  Date: {receipt.date}")
    print(f"  Description: {receipt.description}")
    print(f"  Account: {receipt.account}")
    print(f"  Amount: {receipt.debit_amount} {receipt.currency}")
    print(f"  Status (field): {receipt.status}")
    print(f"  Workflow Status (field): {receipt.workflow_status}")
    print(f"  Reference: {receipt.reference_number}")

print(f"\n3. DUPLICATES CHECK:")
# Check for duplicate entries with same description and date
receipts_by_desc = {}
for receipt in all_receipts:
    key = f"{receipt.date}_{receipt.description}_{receipt.debit_amount}"
    if key not in receipts_by_desc:
        receipts_by_desc[key] = []
    receipts_by_desc[key].append(receipt)

duplicates_found = False
for key, receipts in receipts_by_desc.items():
    if len(receipts) > 1:
        print(f"\nDUPLICATE FOUND: {key}")
        print(f"Count: {len(receipts)}")
        for r in receipts:
            print(f"  - ID {r.id}: Status={r.status}, Workflow={r.workflow_status}")
        duplicates_found = True

if not duplicates_found:
    print("No duplicates found")

print(f"\n4. SUMMARY:")
print(f"Total receipts: {all_receipts.count()}")
print(f"Status=DRAFT: {all_receipts.filter(status='DRAFT').count()}")
print(f"Workflow=AUTHORIZED: {all_receipts.filter(workflow_status='AUTHORIZED').count()}")