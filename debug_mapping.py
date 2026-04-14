#!/usr/bin/env python3
import os
import sys
import django
from decimal import Decimal

sys.path.insert(0, '/var/www/tradifyerp')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tradifyerp.settings')
django.setup()

from accounting.models import InternationalTransferTracking
from shareholder.models import Stakeholder, ShareholderInvestmentLimit

output = []

# Pristine Planet entity
entity_id = 9

output.append("=" * 80)
output.append("DEBUG: INTERNATIONAL TRANSFER MAPPING FOR PRISTINE PLANET")
output.append("=" * 80)

# Step 1: Get all international transfers
all_transfers = InternationalTransferTracking.objects.filter(
    transfer_status__in=['PENDING_ABROAD', 'IN_TRANSIT', 'RECEIVED_LOCALLY', 'CONVERTED']
).select_related('capital_contribution__stakeholder')

output.append(f"\nTotal international transfers: {all_transfers.count()}")

# Step 2: Build the pending_in_foreign_bank_by_stakeholder dict (same logic as view)
pending_in_foreign_bank_by_stakeholder = {}

output.append("\nProcessing transfers:")
for i, transfer in enumerate(all_transfers):
    transfer_stakeholder = transfer.capital_contribution.stakeholder
    destination_amount = transfer.destination_amount
    
    output.append(f"\n  Transfer {i+1}:")
    output.append(f"    - Transfer Stakeholder: {transfer_stakeholder.first_name} {transfer_stakeholder.last_name} ({transfer_stakeholder.email})")
    output.append(f"    - Transfer Stakeholder ID: {transfer_stakeholder.id}")
    output.append(f"    - Transfer Stakeholder Entity ID: {transfer_stakeholder.entity_id}")
    output.append(f"    - Destination Amount: {destination_amount}")
    
    # Find matching stakeholder in target entity
    matching_stakeholder = Stakeholder.objects.filter(
        entity_id=entity_id,
        email=transfer_stakeholder.email
    ).first()
    
    if matching_stakeholder:
        output.append(f"    - MATCH FOUND in entity {entity_id}: ID {matching_stakeholder.id}")
        target_stakeholder = matching_stakeholder
    else:
        output.append(f"    - NO MATCH in entity {entity_id}, using transfer stakeholder ID {transfer_stakeholder.id}")
        target_stakeholder = transfer_stakeholder
    
    target_stakeholder_id = target_stakeholder.id
    
    if target_stakeholder_id not in pending_in_foreign_bank_by_stakeholder:
        pending_in_foreign_bank_by_stakeholder[target_stakeholder_id] = Decimal('0')
    if destination_amount:
        pending_in_foreign_bank_by_stakeholder[target_stakeholder_id] += Decimal(str(destination_amount))
    
    output.append(f"    - Using stakeholder ID: {target_stakeholder_id}")
    output.append(f"    - Current total for ID {target_stakeholder_id}: {pending_in_foreign_bank_by_stakeholder[target_stakeholder_id]}")

# Step 3: Check what investment limits exist for the target entity
output.append("\n" + "=" * 80)
output.append("INVESTMENT LIMITS IN PRISTINE PLANET:")
output.append("=" * 80)

limits = ShareholderInvestmentLimit.objects.filter(entity_id=entity_id, is_active=True)
output.append(f"\nTotal investment limits: {limits.count()}\n")

target_names = ['Rafi', 'Sanaullah', 'Atif', 'Safi']

for limit in limits:
    sh_name = f"{limit.stakeholder.first_name} {limit.stakeholder.last_name}"
    
    if any(target in sh_name for target in target_names):
        sh_id = limit.stakeholder.id
        pending_amount = pending_in_foreign_bank_by_stakeholder.get(sh_id, Decimal('0'))
        
        output.append(f"{sh_name}:")
        output.append(f"  - Stakeholder ID: {sh_id}")
        output.append(f"  - Pending Amount from dict: {pending_amount}")
        output.append(f"  - Would display: {'YES' if (pending_amount and pending_amount > 0) else 'NO (showing —)'}")
        output.append()

output.append("=" * 80)
output.append("PENDLING IN FOREIGN BANK DICT (FINAL):")
output.append("=" * 80)
output.append("Keys in dict: " + str(list(pending_in_foreign_bank_by_stakeholder.keys())))
for k, v in pending_in_foreign_bank_by_stakeholder.items():
    output.append(f"  {k}: {v}")

# Write output to file
with open('/tmp/debug_mapping.txt', 'w') as f:
    f.write('\n'.join(output))

print("Debug output written to /tmp/debug_mapping.txt")
