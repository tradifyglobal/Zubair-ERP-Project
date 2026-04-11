#!/usr/bin/env python
"""Check which entity the international transfers belong to"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings_production')
sys.path.insert(0, '/var/www/tradifyerp')
django.setup()

from accounting.models import InternationalTransferTracking, Entity

# Get international transfers for Pristine Planet
pristine = Entity.objects.get(name='Pristine Planet')

transfers = InternationalTransferTracking.objects.filter(
    capital_contribution__entity=pristine
)

print(f"International transfers for Pristine Planet (Entity ID: {pristine.id}):\n")

for transfer in transfers[:5]:
    cc = transfer.capital_contribution
    stakeholder = cc.stakeholder
    print(f"Transfer ID: {transfer.id}")
    print(f"  Capital Contribution Entity: {cc.entity.name} (ID: {cc.entity.id})")
    print(f"  Stakeholder: {stakeholder.first_name} {stakeholder.last_name} (ID: {stakeholder.id})")
    print(f"  Stakeholder Entity: {stakeholder.entity.name if stakeholder.entity else 'NO ENTITY'} (ID: {stakeholder.entity.id if stakeholder.entity else 'N/A'})")
    print()
