#!/usr/bin/env python3
"""
Verify the fix: Show all stakeholders' contribution status after the change
"""

import os
import django
import sys
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
sys.path.insert(0, '/var/www/tradifyerp')
django.setup()

from accounting.models import CapitalContribution, Entity, CashReceiptLine

entity = Entity.objects.filter(name__icontains='Pristine').first()

print(f"\n{'='*80}")
print(f"VERIFICATION: Capital Contributions & Cash Receipts")
print(f"Entity: {entity.name}")
print(f"{'='*80}")

# Get all contributions
all_contrib = CapitalContribution.objects.filter(entity=entity).select_related('stakeholder')

# Group by status
completed = all_contrib.filter(status='COMPLETED')
pending = all_contrib.filter(status='PENDING')

completed_total = sum(
    [Decimal(str(c.amount_company_currency or 0)) for c in completed],
    Decimal('0')
)
pending_total = sum(
    [Decimal(str(c.amount_company_currency or 0)) for c in pending],
    Decimal('0')
)

print(f"\nCOMPLETED CONTRIBUTIONS: {completed.count()} items = ₹{completed_total:,.2f}")
print(f"PENDING CONTRIBUTIONS:  {pending.count()} items = ₹{pending_total:,.2f}")
print(f"TOTAL:                  {all_contrib.count()} items = ₹{completed_total + pending_total:,.2f}")

# By stakeholder
from collections import defaultdict
by_stakeholder = defaultdict(lambda: {'completed': 0, 'pending': 0, 'completed_amt': Decimal('0'), 'pending_amt': Decimal('0')})

for contrib in all_contrib:
    sh_name = contrib.stakeholder.full_name
    amount = Decimal(str(contrib.amount_company_currency or 0))
    
    if contrib.status == 'COMPLETED':
        by_stakeholder[sh_name]['completed'] += 1
        by_stakeholder[sh_name]['completed_amt'] += amount
    else:
        by_stakeholder[sh_name]['pending'] += 1
        by_stakeholder[sh_name]['pending_amt'] += amount

print(f"\n{'STAKEHOLDER':<25} {'COMPLETED':<30} {'PENDING':<30}")
print("-" * 85)

for sh_name in sorted(by_stakeholder.keys()):
    data = by_stakeholder[sh_name]
    comp_str = f"{data['completed']} items = ₹{data['completed_amt']:,.2f}"
    pend_str = f"{data['pending']} items = ₹{data['pending_amt']:,.2f}" if data['pending'] > 0 else "-"
    print(f"{sh_name:<25} {comp_str:<30} {pend_str:<30}")

# Get total cash receipts
receipts = CashReceiptLine.objects.filter(entity=entity, status='POSTED')
receipt_total = sum(
    [Decimal(str(r.debit_amount or 0)) for r in receipts],
    Decimal('0')
)

print(f"\n{'='*80}")
print(f"COMPARISON TO CASH RECEIPTS")
print(f"{'='*80}")
print(f"Completed Contributions:  ₹{completed_total:,.2f}")
print(f"Posted Cash Receipts:     ₹{receipt_total:,.2f}")

discrepancy = completed_total - receipt_total
if discrepancy == 0:
    print(f"Status:                   ✓ MATCH - No discrepancy!")
else:
    print(f"Discrepancy:              {discrepancy:,.2f}")
    if discrepancy > 0:
        print(f"Status:                   ⚠️  More contributions recorded than cash received")
    else:
        print(f"Status:                   ⚠️  More cash received than contributions recorded")
