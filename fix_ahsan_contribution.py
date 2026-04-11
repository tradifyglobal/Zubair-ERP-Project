#!/usr/bin/env python3
"""
Fix Ahsan Ali Khan's contributions:
- Mark the unreceived ₹300,000 contribution as PENDING instead of COMPLETED
- Keep the 4 ₹100,000 + 1 ₹300,000 (total ₹700,000) as COMPLETED
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

# Get Ahsan Ali Khan's contributions
from accounting.models import Stakeholder
ahsan = Stakeholder.objects.filter(
    entity=entity,
    first_name__icontains='Ahsan'
).first()

if not ahsan:
    print("Error: Ahsan not found")
    # Try searching by email or name contains
    all_stakeholders = Stakeholder.objects.filter(entity=entity)
    print(f"Available stakeholders: {[(s.first_name, s.last_name, s.id) for s in all_stakeholders]}")
    sys.exit(1)

print(f"\nStakeholder: {ahsan.full_name}")
print("-" * 80)

# Get all his COMPLETED contributions
completed = CapitalContribution.objects.filter(
    stakeholder=ahsan,
    status='COMPLETED',
    entity=entity
).order_by('contribution_date')

print(f"\nFound {completed.count()} COMPLETED contributions:")
for idx, contrib in enumerate(completed, 1):
    print(f"  {idx}. ₹{contrib.amount_company_currency:,.2f} (Date: {contrib.contribution_date})")

# Find the one without a matching receipt
# Get cash receipts for this stakeholder
from accounting.models import CashReceiptLine
receipts = CashReceiptLine.objects.filter(
    stakeholder=ahsan,
    status='POSTED'
)

receipt_amounts = [Decimal(str(r.debit_amount or 0)) for r in receipts]
contrib_amounts = [Decimal(str(c.amount_company_currency or 0)) for c in completed]

print(f"\nPosted receipts total: ₹{sum(receipt_amounts):,.2f}")
print(f"Contributions total: ₹{sum(contrib_amounts):,.2f}")
print(f"Gap: ₹{sum(contrib_amounts) - sum(receipt_amounts):,.2f}")

# Find the unreceived contribution
# It should be the one that doesn't match any receipt
unreceived = None

# Sort to find the unpaired one
# Since we have: 100k, 100k, 100k, 100k, 300k, 300k
# And receipts: 100k, 100k, 100k, 100k, 300k (one 300k missing)

# Let's find by counting
from collections import Counter
contrib_counter = Counter(contrib_amounts)
receipt_counter = Counter(receipt_amounts)

print(f"\nContribution amounts: {dict(contrib_counter)}")
print(f"Receipt amounts: {dict(receipt_counter)}")

# Find the amount that has more in contributions than receipts
extra_amount = None
for amount, count in contrib_counter.items():
    if receipt_counter.get(amount, 0) < count:
        extra_amount = amount
        break

if extra_amount:
    print(f"\nFound extra contribution of ₹{extra_amount:,.2f} without matching receipt")
    
    # Get the contribution with this amount that was last added (most likely the unreceived one)
    unreceived = completed.filter(
        amount_company_currency=extra_amount
    ).order_by('-contribution_date').first()
    
    if unreceived:
        print(f"\nChanging to PENDING: ₹{unreceived.amount_company_currency:,.2f} (Date: {unreceived.contribution_date})")
        
        # Update the status
        unreceived.status = 'PENDING'
        unreceived.updated_at = timezone.now()
        unreceived.save()
        
        print(f"✓ Updated status from COMPLETED to PENDING")
        
        # Verify
        print(f"\n" + "=" * 80)
        print("VERIFICATION")
        print("-" * 80)
        
        completed_after = CapitalContribution.objects.filter(
            stakeholder=ahsan,
            status='COMPLETED',
            entity=entity
        )
        
        completed_total = sum(
            [Decimal(str(c.amount_company_currency or 0)) for c in completed_after],
            Decimal('0')
        )
        
        pending_after = CapitalContribution.objects.filter(
            stakeholder=ahsan,
            status='PENDING',
            entity=entity
        )
        
        pending_total = sum(
            [Decimal(str(c.amount_company_currency or 0)) for c in pending_after],
            Decimal('0')
        )
        
        print(f"Completed contributions now: {completed_after.count()} items = ₹{completed_total:,.2f}")
        print(f"Pending contributions now: {pending_after.count()} items = ₹{pending_total:,.2f}")
        print(f"Total: ₹{completed_total + pending_total:,.2f}")
        
        print(f"\n✓ Successfully fixed! Ahsan's completed investments are now ₹{completed_total:,.2f}")
else:
    print("\nError: Could not identify the unreceived contribution")
