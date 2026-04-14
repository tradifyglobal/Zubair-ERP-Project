#!/usr/bin/env python
"""Check if InvestmentLimit records exist"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings_production')
sys.path.insert(0, '/var/www/tradifyerp')
django.setup()

from accounting.models import (
    ShareholderInvestmentLimit, 
    CapitalContribution,
    Entity, 
    Stakeholder
)

entities = Entity.objects.all()
for entity in entities:
    limits = ShareholderInvestmentLimit.objects.filter(entity=entity, is_active=True)
    print(f"\n{entity.name} (ID: {entity.id}):")
    print(f"  InvestmentLimit records: {limits.count()}")
    
    # Also check capital contributions
    contributions = CapitalContribution.objects.filter(entity=entity, workflow_status='APPROVED')
    print(f"  Approved Capital Contributions: {contributions.count()}")
    
    if limits.count() > 0:
        for limit in limits:
            print(f"    - {limit.stakeholder.first_name} {limit.stakeholder.last_name}")
