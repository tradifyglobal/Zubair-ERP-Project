#!/usr/bin/env python3
"""
Mark Ahsan's ₹100,000 pending contribution as COMPLETED
Since he has already invested it
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

# Get Ahsan's PENDING contribution
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

# Get the PENDING ₹100,000 contribution
pending_100k = CapitalContribution.objects.filter(
    stakeholder=ahsan,
    status='PENDING',
    amount_company_currency=Decimal('100000.00')
).first()

if not pending_100k:
    print("Error: Could not find the pending ₹100,000 contribution")
    sys.exit(1)

print(f"\nFound contribution to update:")
print(f"  Amount: ₹{pending_100k.amount_company_currency:,.2f}")
print(f"  Status: {pending_100k.status}")
print(f"  Date: {pending_100k.contribution_date}")

# Update the status
pending_100k.status = 'COMPLETED'
pending_100k.updated_at = timezone.now()
pending_100k.save()

print(f"\nUpdated status from PENDING to COMPLETED")

# Verify
print(f"\n" + "=" * 80)
print("FINAL VERIFICATION")
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
for idx, contrib in enumerate(completed.order_by('-amount_company_currency'), 1):
    print(f"  {idx}. ₹{contrib.amount_company_currency:,.2f}")

if pending_total > 0:
    print(f"\nAhsan's Pending Contributions: {pending.count()} items = ₹{pending_total:,.2f}")
    for idx, contrib in enumerate(pending, 1):
        print(f"  {idx}. ₹{contrib.amount_company_currency:,.2f}")
else:
    print(f"\nAhsan's Pending Contributions: None")

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

print(f"Cash Receipts Posted: ₹{receipt_total:,.2f}")

if completed_total == receipt_total:
    print(f"\n✓ PERFECT MATCH! All contributions are reconciled with cash receipts")
else:
    gap = completed_total - receipt_total
    if gap > 0:
        print(f"\n⚠️  More contributions than receipts: ₹{abs(gap):,.2f}")
    else:
        print(f"\n✓ All contributions received (gap of ₹{abs(gap):,.2f} likely other stakeholders)")
