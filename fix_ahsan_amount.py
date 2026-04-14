#!/usr/bin/env python3
"""
Fix Ahsan's 5th contribution: Change ₹300,000 to ₹100,000
"""

import os
import django
import sys
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
sys.path.insert(0, '/var/www/tradifyerp')
django.setup()

from accounting.models import CapitalContribution, Entity
from django.utils import timezone

entity = Entity.objects.filter(name__icontains='Pristine').first()
if not entity:
    print("Error: Could not find entity")
    sys.exit(1)

print(f"Entity: {entity.name}")
print("=" * 80)

# Get Ahsan's contributions
from accounting.models import Stakeholder
ahsan = Stakeholder.objects.filter(
    entity=entity,
    first_name__icontains='Ahsan'
).first()

if not ahsan:
    print("Error: Ahsan not found")
    sys.exit(1)

print(f"Stakeholder: {ahsan.full_name}")
print("-" * 80)

# Get the PENDING ₹300,000 contribution (the 5th one)
pending_300k = CapitalContribution.objects.filter(
    stakeholder=ahsan,
    status='PENDING',
    amount_company_currency=Decimal('300000.00')
).first()

if not pending_300k:
    print("Error: Could not find the pending ₹300,000 contribution")
    sys.exit(1)

print(f"\nFound contribution to update:")
print(f"  Current Amount: ₹{pending_300k.amount_company_currency:,.2f}")
print(f"  Status: {pending_300k.status}")
print(f"  Date: {pending_300k.contribution_date}")

# Update the amount
old_amount = Decimal(str(pending_300k.amount_company_currency))
new_amount = Decimal('100000.00')

# Update the base 'amount' field (amount_company_currency is calculated from amount * exchange_rate)
pending_300k.amount = new_amount
pending_300k.updated_at = timezone.now()
pending_300k.save()

print(f"\nUpdated to:")
print(f"  New Amount: ₹{pending_300k.amount_company_currency:,.2f}")
print(f"  Change: ₹{old_amount:,.2f} → ₹{new_amount:,.2f}")

# Verify
print(f"\n" + "=" * 80)
print("VERIFICATION")
print("-" * 80)

completed = CapitalContribution.objects.filter(
    stakeholder=ahsan,
    status='COMPLETED'
)

pending = CapitalContribution.objects.filter(
    stakeholder=ahsan,
    status='PENDING'
)

completed_total = sum(
    [Decimal(str(c.amount_company_currency or 0)) for c in completed],
    Decimal('0')
)

pending_total = sum(
    [Decimal(str(c.amount_company_currency or 0)) for c in pending],
    Decimal('0')
)

print(f"\nAhsan's Completed Contributions: {completed.count()} items = ₹{completed_total:,.2f}")
for idx, contrib in enumerate(completed, 1):
    print(f"  {idx}. ₹{contrib.amount_company_currency:,.2f}")

print(f"\nAhsan's Pending Contributions: {pending.count()} items = ₹{pending_total:,.2f}")
for idx, contrib in enumerate(pending, 1):
    print(f"  {idx}. ₹{contrib.amount_company_currency:,.2f}")

overall_total = completed_total + pending_total
print(f"\nTotal: ₹{overall_total:,.2f}")

# Compare with cash receipts
from accounting.models import CashReceiptLine
receipts = CashReceiptLine.objects.filter(
    stakeholder=ahsan,
    status='POSTED'
)

receipt_total = sum(
    [Decimal(str(r.debit_amount or 0)) for r in receipts],
    Decimal('0')
)

print(f"\nCash Receipts Posted: ₹{receipt_total:,.2f}")

if completed_total == receipt_total:
    print(f"✓ MATCH! Completed contributions now match cash receipts")
else:
    gap = completed_total - receipt_total
    print(f"Discrepancy: ₹{gap:,.2f}")
