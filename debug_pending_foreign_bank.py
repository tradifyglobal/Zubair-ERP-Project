#!/usr/bin/env python
"""Debug script to check why Pending in Foreign Bank data is not showing"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings_production')
sys.path.insert(0, '/var/www/tradifyerp')
django.setup()

from accounting.models import (
    InternationalTransferTracking, 
    CapitalContribution, 
    Entity, 
    Stakeholder
)
from decimal import Decimal

# Get all entities
entities = Entity.objects.all()
print(f"Total entities: {entities.count()}")
print()

for entity in entities:
    print(f"=" * 80)
    print(f"Entity: {entity.name} (ID: {entity.id})")
    print(f"=" * 80)
    
    # Check capital contributions
    contributions = CapitalContribution.objects.filter(
        entity=entity,
        workflow_status='APPROVED'
    )
    print(f"\nApproved Capital Contributions: {contributions.count()}")
    
    # Check international transfers
    transfers = InternationalTransferTracking.objects.filter(
        capital_contribution__entity=entity,
        transfer_status__in=['PENDING_ABROAD', 'IN_TRANSIT', 'RECEIVED_LOCALLY', 'CONVERTED']
    ).select_related('capital_contribution__stakeholder')
    
    print(f"Pending International Transfers: {transfers.count()}")
    
    if transfers.count() == 0:
        print("\n  ⚠️ NO PENDING TRANSFERS FOUND!")
        print("\n  Checking all transfers (regardless of status):")
        all_transfers = InternationalTransferTracking.objects.filter(
            capital_contribution__entity=entity
        ).select_related('capital_contribution__stakeholder')
        print(f"  Total transfers (all statuses): {all_transfers.count()}")
        for t in all_transfers[:5]:
            print(f"    - Status: {t.transfer_status}, Amount: {t.destination_amount}")
    else:
        print("\n  Transfer Details:")
        pending_by_stakeholder = {}
        for transfer in transfers:
            if transfer.capital_contribution and transfer.capital_contribution.stakeholder:
                stakeholder = transfer.capital_contribution.stakeholder
                stakeholder_id = stakeholder.id
                stakeholder_name = f"{stakeholder.first_name} {stakeholder.last_name}"
                
                if stakeholder_id not in pending_by_stakeholder:
                    pending_by_stakeholder[stakeholder_id] = {
                        'name': stakeholder_name,
                        'total': Decimal('0'),
                        'count': 0
                    }
                
                pending_by_stakeholder[stakeholder_id]['total'] += Decimal(str(transfer.destination_amount or 0))
                pending_by_stakeholder[stakeholder_id]['count'] += 1
                
                print(f"    - {stakeholder_name}: {transfer.destination_amount} INR ({transfer.transfer_status})")
            else:
                print(f"    ⚠️  Transfer with NO stakeholder link!")
        
        print(f"\n  Aggregated by Stakeholder:")
        for stakeholder_id, data in pending_by_stakeholder.items():
            print(f"    - {data['name']}: ₹{data['total']} ({data['count']} transfers)")

print("\n" + "=" * 80)
print("DEBUG COMPLETE")
print("=" * 80)
