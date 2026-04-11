import os
import sys
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "TradifyERP.settings_production")
sys.path.insert(0, '/var/www/tradifyerp')
django.setup()

from accounting.models import Entity, InternationalTransferTracking, Stakeholder

# Get entities
internal = Entity.objects.get(id=6)  # Internal
pristine = Entity.objects.get(id=9)  # Pristine Planet

print("=== PRISTINE PLANET STAKEHOLDERS ===")
pristine_stakeholders = Stakeholder.objects.filter(entity=pristine)
for s in pristine_stakeholders:
    print(f"  ID {s.id}: {s.first_name} {s.last_name} ({s.email})")

print("\n=== INTERNATIONAL TRANSFERS (Source Stakeholder Emails) ===")
intl_transfers = InternationalTransferTracking.objects.filter(
    transfer_status__in=['PENDING_ABROAD', 'IN_TRANSIT', 'RECEIVED_LOCALLY', 'CONVERTED']
).select_related('capital_contribution__stakeholder', 'capital_contribution__entity')

for transfer in intl_transfers:
    src_stake = transfer.capital_contribution.stakeholder
    src_entity = transfer.capital_contribution.entity
    print(f"  Entity: {src_entity.name}, Stakeholder: {src_stake.full_name} ({src_stake.email})")
    
    # Try to find matching in Pristine Planet
    match = Stakeholder.objects.filter(entity=pristine, email=src_stake.email).first()
    if match:
        print(f"    ✓ MATCHED: Pristine Planet ID {match.id}: {match.full_name}")
    else:
        print(f"    ✗ NO MATCH for email: {src_stake.email}")
