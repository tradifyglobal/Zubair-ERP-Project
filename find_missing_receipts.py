#!/usr/bin/env python3
"""
Find the exact contribution(s) that are marked COMPLETED but don't have cash receipts
"""

import os
import django
import sys
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
sys.path.insert(0, '/var/www/tradifyerp')
django.setup()

from accounting.models import CapitalContribution, CashReceiptLine, Entity
from django.db.models import Sum

entity = Entity.objects.filter(name__icontains='Pristine').first()
if not entity:
    print("Error: Could not find entity")
    sys.exit(1)

print(f"Entity: {entity.name}")
print("=" * 80)

# Get all completed contributions WITH details
completed = CapitalContribution.objects.filter(
    entity=entity,
    status='COMPLETED'
).select_related('stakeholder')

print(f"\nCOMPLETED CONTRIBUTIONS ({completed.count()}):")
print("-" * 80)

# Get all posted cash receipts by stakeholder ID
receipts_by_stakeholder_id = {}
for receipt in CashReceiptLine.objects.filter(entity=entity, status='POSTED').select_related('stakeholder'):
    sh_id = receipt.stakeholder.id if receipt.stakeholder else None
    if sh_id:
        if sh_id not in receipts_by_stakeholder_id:
            receipts_by_stakeholder_id[sh_id] = []
        receipts_by_stakeholder_id[sh_id].append({
            'ref': receipt.reference_number,
            'amount': Decimal(str(receipt.debit_amount or 0))
        })

# Print stakeholder-by-stakeholder comparison
for contribution in completed.order_by('stakeholder__first_name', 'stakeholder__last_name'):
    stakeholder = contribution.stakeholder
    sh_id = stakeholder.id
    sh_name = stakeholder.full_name
    
    # Get all contributions for this stakeholder
    sh_contributions = completed.filter(stakeholder_id=sh_id)
    contrib_amounts = [Decimal(str(c.amount_company_currency or 0)) for c in sh_contributions]
    contrib_total = sum(contrib_amounts, Decimal('0'))
    
    # Get receipts for this stakeholder
    receipts = receipts_by_stakeholder_id.get(sh_id, [])
    receipt_amounts = [r['amount'] for r in receipts]
    receipt_total = sum(receipt_amounts, Decimal('0'))
    
    gap = contrib_total - receipt_total
    
    match = "✓ MATCH" if gap == 0 else f"✗ MISMATCH (Gap: ₹{gap:,.2f})"
    
    print(f"\n{sh_name}:")
    print(f"  Contributions ({len(contrib_amounts)}): ₹{contrib_total:,.2f}")
    for idx, contribution in enumerate(sh_contributions, 1):
        print(f"    {idx}. ₹{contribution.amount_company_currency:,.2f} (Date: {contribution.contribution_date})")
    
    print(f"  Receipts ({len(receipts)}): ₹{receipt_total:,.2f}")
    for receipt in receipts:
        print(f"    {receipt['ref']}: ₹{receipt['amount']:,.2f}")
    
    print(f"  {match}")

print("\n" + "=" * 80)
print("\nRECOMMENDATION:")
print("-" * 80)

gaps_found = False
for contribution in completed:
    stakeholder = contribution.stakeholder
    sh_id = stakeholder.id
    sh_name = stakeholder.full_name
    
    # Get all contributions for this stakeholder
    sh_contributions = completed.filter(stakeholder_id=sh_id)
    contrib_total = sum(
        [Decimal(str(c.amount_company_currency or 0)) for c in sh_contributions],
        Decimal('0')
    )
    
    # Get receipts for this stakeholder
    receipts = receipts_by_stakeholder_id.get(sh_id, [])
    receipt_total = sum([r['amount'] for r in receipts], Decimal('0'))
    
    if contrib_total != receipt_total:
        if not gaps_found:
            gaps_found = True
        gap = contrib_total - receipt_total
        print(f"\n⚠️  {sh_name}: Gap of ₹{gap:,.2f}")
        if gap > 0:
            print(f"   ACTION: Either:")
            print(f"   1. Create a new cash receipt for ₹{gap:,.2f}")
            print(f"   2. Or mark {abs(gap)} contribution(s) as PENDING instead of COMPLETED")
        break  # Only show first mismatch to avoid duplicates

if not gaps_found:
    print("\n✓ No gaps found - all contributions have matching cash receipts")
