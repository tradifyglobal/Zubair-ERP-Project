#!/usr/bin/env python
"""List all stakeholders with investment limits and their pending amounts"""

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
    Entity,
    Stakeholder
)

entity = Entity.objects.get(name='Pristine Planet')

# Get all international transfers with pending amounts
pending_map = {}
intl_transfers = InternationalTransferTracking.objects.filter(
    capital_contribution__entity=entity,
    transfer_status__in=['PENDING_ABROAD', 'IN_TRANSIT', 'RECEIVED_LOCALLY', 'CONVERTED']
).select_related('capital_contribution__stakeholder')

print(f"Entity: {entity.name}")
print(f"Total international transfers with pending status: {intl_transfers.count()}\n")

for transfer in intl_transfers:
    stakeholder = transfer.capital_contribution.stakeholder
    sid = stakeholder.id
    if sid not in pending_map:
        pending_map[sid] = {'name': f"{stakeholder.first_name} {stakeholder.last_name}", 'amount': Decimal('0')}
    pending_map[sid]['amount'] += Decimal(str(transfer.destination_amount or 0))

print("Pending amounts by stakeholder:")
for sid, data in pending_map.items():
    print(f"  - {data['name']} (ID: {sid}): ₹{data['amount']}")

# Now check investment limits
print(f"\n\nInvestment Limits in Pristine Planet:")
limits = ShareholderInvestmentLimit.objects.filter(entity=entity, is_active=True)
print(f"Total limits: {limits.count()}\n")

for limit in limits:
    pending = pending_map.get(limit.stakeholder.id, {}).get('amount', Decimal('0'))
    status = "✓ HAS PENDING" if pending > 0 else "—"
    print(f"  {limit.stakeholder.first_name} {limit.stakeholder.last_name} (ID: {limit.stakeholder.id}): {pending_map.get(limit.stakeholder.id, {}).get('amount', 0)} {status}")
