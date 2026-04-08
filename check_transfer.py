#!/usr/bin/env python
import os
import sys
import django

# Add project to path
sys.path.insert(0, '/var/www/tradifyerp')
os.chdir('/var/www/tradifyerp')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings_production')
django.setup()

from accounting.models import CapitalContribution, InternationalTransferTracking

# Check contribution 282
try:
    contrib_282 = CapitalContribution.objects.get(id=282)
    print(f"Contribution 282 FOUND")
    print(f"  Entity ID: {contrib_282.entity_id}")
    print(f"  Entity Name: {contrib_282.entity.name if contrib_282.entity else 'NONE'}")
    print(f"  Stakeholder: {contrib_282.stakeholder.full_name if contrib_282.stakeholder else 'NONE'}")
    
    # Check for transfer
    try:
        transfer = contrib_282.international_transfer
        if transfer:
            print(f"  Transfer FOUND: ID {transfer.id}, Status: {transfer.transfer_status}")
        else:
            print(f"  No transfer tracking")
    except:
        print(f"  No transfer tracking (exception)")
except CapitalContribution.DoesNotExist:
    print("Contribution 282 NOT FOUND")

# Count all transfers
all_transfers = InternationalTransferTracking.objects.all()
print(f"\nTotal transfers in DB: {all_transfers.count()}")

# Check filters
transfers_pristine = InternationalTransferTracking.objects.filter(capital_contribution__entity_id=9)
print(f"Transfers for entity 9 (Pristine-Planet-01): {transfers_pristine.count()}")

# List all transfers
print("\nAll transfers:")
for t in all_transfers:
    contrib = t.capital_contribution
    print(f"  ID: {t.id}, Contrib ID: {contrib.id}, Entity: {contrib.entity_id}, Status: {t.transfer_status}")
