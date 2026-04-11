import os
import sys
import django
from django.conf import settings
from decimal import Decimal

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "TradifyERP.settings_production")
sys.path.insert(0, '/var/www/tradifyerp')
django.setup()

from accounting.models import ShareholderInvestmentLimit, InternationalTransferTracking, CapitalContribution, Entity, Stakeholder
from django.db.models import Sum, Q

# Get Pristine Planet entity
entity = Entity.objects.get(id=9)  

# Get the same data the view would process
intl_transfers = InternationalTransferTracking.objects.filter(
    capital_contribution__entity=entity,
    transfer_status__in=['PENDING_ABROAD', 'IN_TRANSIT', 'RECEIVED_LOCALLY', 'CONVERTED']
).select_related('capital_contribution__stakeholder')

print(f"Total international transfers for {entity.name}: {intl_transfers.count()}")
print("\nChecking email-based matching:")

pending_in_foreign_bank_by_stakeholder = {}
for transfer in intl_transfers:
    transfer_stakeholder = transfer.capital_contribution.stakeholder
    destination_amount = transfer.destination_amount
    
    print(f"\n  Transfer: {transfer_stakeholder.email} (original ID: {transfer_stakeholder.id})")
    print(f"    Destination Amount: {destination_amount}")
    
    # EMAIL-BASED MATCHING
    matching_stakeholder = Stakeholder.objects.filter(
        entity=entity,
        email=transfer_stakeholder.email
    ).first()
    
    if matching_stakeholder:
        print(f"    ✓ MATCHED to {entity.name} Stakeholder ID: {matching_stakeholder.id}")
        target_stakeholder_id = matching_stakeholder.id
    else:
        print(f"    ✗ NO MATCH FOUND - using original ID: {transfer_stakeholder.id}")
        target_stakeholder_id = transfer_stakeholder.id
    
    if target_stakeholder_id not in pending_in_foreign_bank_by_stakeholder:
        pending_in_foreign_bank_by_stakeholder[target_stakeholder_id] = Decimal('0')
    if destination_amount:
        pending_in_foreign_bank_by_stakeholder[target_stakeholder_id] += Decimal(str(destination_amount))

print(f"\n\n===== FINAL MAPPING =====")
print(f"Pending in Foreign Bank Dictionary: {pending_in_foreign_bank_by_stakeholder}")

# Now check investment limits
investment_limits = ShareholderInvestmentLimit.objects.filter(entity=entity).select_related('stakeholder')
print(f"\n\nInvestment Limits for {entity.name}:")
for limit in investment_limits:
    pending_amount = pending_in_foreign_bank_by_stakeholder.get(limit.stakeholder.id, Decimal('0'))
    print(f"  {limit.stakeholder.full_name} (ID: {limit.stakeholder.id}): Pending = ₹{pending_amount}")
