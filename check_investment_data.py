#!/usr/bin/env python
"""Check the exact investment_data that's passed to the template"""

import os
import sys
import django
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings_production')
sys.path.insert(0, '/var/www/tradifyerp')
django.setup()

from accounting.models import (
    ShareholderInvestmentLimit,
    InternationalTransferTracking,
    CapitalContribution,
    Entity,
    Account,
    LedgerEntry,
    Stakeholder
)
from django.db.models import Sum, Q

# Simulate ShareholderInvestmentReportView.get_context_data() for Pristine Planet
entity = Entity.objects.get(name='Pristine Planet')
print(f"Entity: {entity.name} (ID: {entity.id})\n")

def normalize_name(name):
    if not name:
        return ''
    value = ' '.join(str(name).split())
    if value.lower().endswith(' - capital'):
        value = value[:-10]
    return value.strip().lower()

# Get international transfers
pending_in_foreign_bank_by_stakeholder = {}
intl_transfers = InternationalTransferTracking.objects.filter(
    capital_contribution__entity=entity,
    transfer_status__in=['PENDING_ABROAD', 'IN_TRANSIT', 'RECEIVED_LOCALLY', 'CONVERTED']
).select_related('capital_contribution__stakeholder').values_list(
    'capital_contribution__stakeholder_id',
    'destination_amount'
)

print(f"Step 1: Building pending_in_foreign_bank_by_stakeholder")
print(f"  Found {intl_transfers.count()} transfers\n")

for stakeholder_id, destination_amount in intl_transfers:
    if stakeholder_id not in pending_in_foreign_bank_by_stakeholder:
        pending_in_foreign_bank_by_stakeholder[stakeholder_id] = Decimal('0')
    if destination_amount:
        pending_in_foreign_bank_by_stakeholder[stakeholder_id] += Decimal(str(destination_amount))

print(f"Pending amounts aggregated:")
for sid, amount in pending_in_foreign_bank_by_stakeholder.items():
    sh = Stakeholder.objects.get(id=sid)
    print(f"  {sh.first_name} {sh.last_name} (ID: {sid}): ₹{amount}")

# Now iterate through investment limits (what the view does)
print(f"\nStep 2: Processing Investment Limits")
limits = ShareholderInvestmentLimit.objects.filter(entity=entity, is_active=True)
print(f"  Total limits: {limits.count()}\n")

investment_data = []
for i, limit in enumerate(limits):
    pending_foreign_bank = pending_in_foreign_bank_by_stakeholder.get(limit.stakeholder.id, Decimal('0'))
    
    investment_data.append({
        'stakeholder': limit.stakeholder,
        'target_amount': limit.target_investment_amount,
        'pending_in_foreign_bank': pending_foreign_bank,  # <--- THIS KEY
    })
    
    if i < 5 or (pending_foreign_bank > 0):  # Print first 5 and all with pending amounts
        print(f"  {limit.stakeholder.first_name} {limit.stakeholder.last_name}:")
        print(f"    - Stakeholder ID: {limit.stakeholder.id}")
        print(f"    - Target: {limit.target_investment_amount}")
        print(f"    - Pending in Foreign Bank: {pending_foreign_bank}")
        print(f"    - Value > 0? {pending_foreign_bank > 0}")

print(f"\nTotal investment records built: {len(investment_data)}")
print(f"Records with pending_in_foreign_bank > 0: {len([x for x in investment_data if x['pending_in_foreign_bank'] > 0])}")
