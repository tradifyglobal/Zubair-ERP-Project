#!/usr/bin/env python3
import os
import sys
import django

sys.path.insert(0, '/var/www/tradifyerp')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tradifyerp.settings')
django.setup()

from accounting.models import InternationalTransferTracking
from shareholder.models import Stakeholder

print("=" * 80)
print("INTERNATIONAL TRANSFER ANALYSIS")
print("=" * 80)

# Get all international transfers
transfers = InternationalTransferTracking.objects.all()
print(f"\nTotal transfers in database: {transfers.count()}")

# Check what entities they're linked to
for transfer in transfers[:10]:  # Limit to first 10
    print(f"\nTransfer ID: {transfer.id}")
    print(f"  - Capital Contribution ID: {transfer.capital_contribution_id}")
    print(f"  - Entity of CC: {transfer.capital_contribution.entity_id}")
    print(f"  - Stakeholder: {transfer.capital_contribution.stakeholder.email}")
    print(f"  - Status: {transfer.transfer_status}")
    print(f"  - Destination Amount: {transfer.destination_amount}")

print("\n" + "=" * 80)
print("CHECKING PRISTINE PLANET CONTEXT")
print("=" * 80)

entity_id = 9
pristine_stakeholders = Stakeholder.objects.filter(entity_id=entity_id)
print(f"\nStakeholders in entity {entity_id}: {pristine_stakeholders.count()}")

target_emails = ['mohammed.rafi@tradify.com', 'mohammed.sanaullah@tradify.com', 'syed.atif@tradify.com', 'syed.safi@tradify.com']

for email in target_emails[:4]:
    matching = Stakeholder.objects.filter(email=email, entity_id=entity_id).first()
    if matching:
        print(f"  {email}: ID={matching.id} (entity {entity_id})")
    else:
        print(f"  {email}: NOT FOUND in entity {entity_id}")

print("\n" + "=" * 80)
print("CHECKING ALL TRANSFERS FOR PRISTINE STAKEHOLDERS")
print("=" * 80)

# Check transfers linked to these emails
for email in target_emails[:4]:
    # Find stakeholders with this email (regardless of entity)
    stakeholders_with_email = Stakeholder.objects.filter(email=email)
    print(f"\nEmail: {email}")
    print(f"  - Stakeholders with this email: {stakeholders_with_email.count()}")
    
    for sh in stakeholders_with_email:
        print(f"    - ID {sh.id} (entity {sh.entity_id})")
        
        # Find transfers linked to this stakeholder
        transfers_for_sh = InternationalTransferTracking.objects.filter(
            capital_contribution__stakeholder_id=sh.id,
            transfer_status__in=['PENDING_ABROAD', 'IN_TRANSIT', 'RECEIVED_LOCALLY', 'CONVERTED']
        )
        
        if transfers_for_sh.exists():
            total = sum(Decimal(str(t.destination_amount or 0)) for t in transfers_for_sh)
            print(f"      - {transfers_for_sh.count()} transfers, Total: {total}")
        else:
            print(f"      - No transfers")

print("\n" + "=" * 80)

# Also check what we'd get with the new query
print("WITH NEW QUERY (ALL TRANSFERS):")
print("=" * 80)

all_transfers = InternationalTransferTracking.objects.filter(
    transfer_status__in=['PENDING_ABROAD', 'IN_TRANSIT', 'RECEIVED_LOCALLY', 'CONVERTED']
)

print(f"Total transfers found (not filtered by entity): {all_transfers.count()}")

# Group by stakeholder email
from decimal import Decimal
transfers_by_email = {}

for transfer in all_transfers:
    email = transfer.capital_contribution.stakeholder.email
    if email not in transfers_by_email:
        transfers_by_email[email] = Decimal('0')
    if transfer.destination_amount:
        transfers_by_email[email] += Decimal(str(transfer.destination_amount))

for email, total in transfers_by_email.items():
    if any(target in email for target in target_emails):
        print(f"{email}: {total}")

print("\n" + "=" * 80)
