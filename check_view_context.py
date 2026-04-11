#!/usr/bin/env python
"""Check what the investment report view produces"""

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
    LedgerEntry
)
from django.db.models import Sum, Q

# Simulate what the view does for Pristine Planet
entity = Entity.objects.get(name='Pristine Planet')
print(f"Entity: {entity.name} (ID: {entity.id})")
print("=" * 80)

# Build invested amounts from Chart of Accounts (same as view)
def normalize_name(name):
    if not name:
        return ''
    value = ' '.join(str(name).split())
    if value.lower().endswith(' - capital'):
        value = value[:-10]
    return value.strip().lower()

stakeholder_capital_accounts = Account.objects.filter(
    entity=entity,
    account_type='EQUITY',
    is_active=True
).filter(
    Q(account_number__startswith='SHR-') |
    Q(name__iendswith=' - Capital')
)

print(f"Capital Accounts found: {stakeholder_capital_accounts.count()}")

# Get international transfers (this is the key part)
pending_in_foreign_bank_by_stakeholder = {}
intl_transfers = InternationalTransferTracking.objects.filter(
    capital_contribution__entity=entity,
    transfer_status__in=['PENDING_ABROAD', 'IN_TRANSIT', 'RECEIVED_LOCALLY', 'CONVERTED']
).select_related('capital_contribution__stakeholder').values_list(
    'capital_contribution__stakeholder_id',
    'destination_amount'
)

print(f"\nInternational Transfers Query:")
print(f"  Found: {intl_transfers.count()} transfers")

for stakeholder_id, destination_amount in intl_transfers:
    if stakeholder_id not in pending_in_foreign_bank_by_stakeholder:
        pending_in_foreign_bank_by_stakeholder[stakeholder_id] = Decimal('0')
    if destination_amount:
        pending_in_foreign_bank_by_stakeholder[stakeholder_id] += Decimal(str(destination_amount))

print(f"  Aggregated by stakeholder:")
for stakeholder_id, amount in pending_in_foreign_bank_by_stakeholder.items():
    from accounting.models import Stakeholder
    stakeholder = Stakeholder.objects.get(id=stakeholder_id)
    print(f"    - {stakeholder.first_name} {stakeholder.last_name} (ID: {stakeholder_id}): ₹{amount}")

# Now check if these are being used in investment limits
print(f"\nInvestment Limits Check:")
limits = ShareholderInvestmentLimit.objects.filter(entity=entity, is_active=True)
print(f"  Total limits: {limits.count()}")

for limit in limits[:3]:
    pending = pending_in_foreign_bank_by_stakeholder.get(limit.stakeholder.id, Decimal('0'))
    print(f"  - {limit.stakeholder.first_name} {limit.stakeholder.last_name}:")
    print(f"      Stakeholder ID: {limit.stakeholder.id}")
    print(f"      Target: {limit.target_investment_amount}")
    print(f"      Pending in Foreign Bank: ₹{pending}")
