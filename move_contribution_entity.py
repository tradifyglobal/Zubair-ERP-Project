#!/usr/bin/env python
"""Update contribution 282 to belong to Pristine Planet-01 entity"""

import os
import sys
import django

# Add project to path
sys.path.insert(0, '/var/www/tradifyerp')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')

# Setup Django
django.setup()

from accounting.models import CapitalContribution, Entity

# Find Pristine Planet-01 entity
try:
    entity = Entity.objects.get(name='Pristine Planet-01')
    print(f"✓ Found entity: {entity.name} (ID: {entity.id})")
except Entity.DoesNotExist:
    print("✗ Entity 'Pristine Planet-01' not found")
    sys.exit(1)

# Find contribution 282
try:
    contribution = CapitalContribution.objects.get(id=282)
    old_entity = contribution.entity
    print(f"\nCurrent state of contribution 282:")
    print(f"  - Stakeholder: {contribution.stakeholder.name}")
    print(f"  - Amount: {contribution.amount} {contribution.currency.code}")
    print(f"  - Current Entity: {old_entity.name} (ID: {old_entity.id})")
    
    # Update the entity
    contribution.entity = entity
    contribution.save()
    
    print(f"\n✓ Successfully updated contribution 282!")
    print(f"  - Old Entity: {old_entity.name} (ID: {old_entity.id})")
    print(f"  - New Entity: {contribution.entity.name} (ID: {contribution.entity.id})")
    
    # Check transfer tracking
    try:
        transfer = contribution.international_transfer
        print(f"\n✓ Transfer record associated:")
        print(f"  - Transfer ID: {transfer.id}")
        print(f"  - Status: {transfer.transfer_status}")
        print(f"  - Will now appear under entity: {contribution.entity.name}")
    except Exception as e:
        print(f"\nℹ No transfer record found for this contribution (or error: {e})")
        
except CapitalContribution.DoesNotExist:
    print("✗ Contribution 282 not found")
    sys.exit(1)
