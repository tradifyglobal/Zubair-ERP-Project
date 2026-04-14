#!/usr/bin/env python
"""Check which entity owns contribution 282 and its transfer record"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from accounting.models import CapitalContribution, InternationalTransferTracking

try:
    # Get contribution 282
    cc = CapitalContribution.objects.get(id=282)
    print(f"✓ Contribution 282 found")
    print(f"  - Stakeholder: {cc.stakeholder.name}")
    print(f"  - Amount: {cc.amount} {cc.currency.code}")
    print(f"  - Entity ID: {cc.entity_id}")
    print(f"  - Entity Name: {cc.entity.name}")
    
    # Check if transfer exists
    try:
        transfer = cc.international_transfer
        print(f"\n✓ Transfer record found for contribution 282")
        print(f"  - Transfer ID: {transfer.id}")
        print(f"  - Transfer Status: {transfer.transfer_status}")
        print(f"  - Source: {transfer.source_country} ({transfer.source_currency_code})")
        print(f"  - Destination: {transfer.destination_country} ({transfer.destination_currency_code})")
    except InternationalTransferTracking.DoesNotExist:
        print(f"\n✗ No transfer record found for contribution 282")
        
except CapitalContribution.DoesNotExist:
    print(f"✗ Contribution 282 not found")

# Also check transfer 14 directly
print("\n" + "="*60)
try:
    transfer = InternationalTransferTracking.objects.get(id=14)
    print(f"✓ Transfer ID 14 found")
    print(f"  - Linked to Contribution ID: {transfer.capital_contribution_id}")
    print(f"  - Contribution: {transfer.capital_contribution}")
    print(f"  - Entity: {transfer.capital_contribution.entity.name} (ID: {transfer.capital_contribution.entity_id})")
    print(f"  - Transfer Status: {transfer.transfer_status}")
except InternationalTransferTracking.DoesNotExist:
    print(f"✗ Transfer ID 14 not found")
