#!/usr/bin/env python
"""Debug script to check international transfers aggregation."""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from accounting.models import InternationalTransferTracking, Entity
from shareholder.models import Stakeholder
from decimal import Decimal

# Get entity ID 2 (first active entity)
try:
    entity = Entity.objects.filter(is_active=True).first()
    if not entity:
        print("No active entity found!")
        sys.exit(1)
    
    print(f"Entity: {entity.entity_code} - {entity.entity_name}")
    print(f"Entity ID: {entity.id}\n")
    
    # Check transfers with entity filter
    transfers = InternationalTransferTracking.objects.filter(
        capital_contribution__entity=entity,
        transfer_status__in=['PENDING_ABROAD', 'IN_TRANSIT', 'RECEIVED_LOCALLY', 'CONVERTED']
    ).select_related('capital_contribution__stakeholder')
    
    print(f"Transfers with entity filter: {transfers.count()}")
    aggregated = {}
    for t in transfers:
        sh = t.capital_contribution.stakeholder if t.capital_contribution else None
        if sh:
            print(f"  {sh.full_name}: ₹{t.destination_amount} ({t.transfer_status})")
            if sh.id not in aggregated:
                aggregated[sh.id] = Decimal('0')
            aggregated[sh.id] += Decimal(str(t.destination_amount))
    
    print(f"\nAggregated by stakeholder:")
    for stakeholder_id, amount in aggregated.items():
        sh = Stakeholder.objects.get(id=stakeholder_id)
        print(f"  {sh.full_name}: ₹{amount}")
    
    # Check total transfers (all statuses)
    all_transfers = InternationalTransferTracking.objects.filter(
        capital_contribution__entity=entity
    )
    print(f"\nAll transfers for entity: {all_transfers.count()}")
    
    # Check by status
    for status in ['PENDING_ABROAD', 'IN_TRANSIT', 'RECEIVED_LOCALLY', 'CONVERTED', 'POSTED_TO_GL', 'CANCELLED']:
        count = InternationalTransferTracking.objects.filter(
            capital_contribution__entity=entity,
            transfer_status=status
        ).count()
        print(f"  {status}: {count}")
    
except Exception as e:
    import traceback
    print(f"Error: {e}")
    traceback.print_exc()
    sys.exit(1)
