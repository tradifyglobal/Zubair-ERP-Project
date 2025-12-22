#!/usr/bin/env python3
"""Simple database query to check pending amounts"""
import os
import sys
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
os.environ['TIME_ZONE'] = 'UTC'
os.environ['TZ'] = 'UTC'
sys.path.insert(0, '/var/www/tradifyerp')
django.setup()

from django.db.models import Sum
from accounting.models import CapitalContribution, Entity

# Get the current entity (likely INT-001)
entities = Entity.objects.all()
print(f"Entities in DB: {list(entities.values('id', 'name'))}")

for entity in entities:
    pending = CapitalContribution.objects.filter(entity=entity, status='PENDING')
    print(f"\n{entity.name} (ID: {entity.id}):")
    print(f"  Pending count: {pending.count()}")
    
    amount_sum = pending.aggregate(Sum('amount'))['amount__sum'] or 0
    company_sum = pending.aggregate(Sum('amount_company_currency'))['amount_company_currency__sum'] or 0
    
    print(f"  Sum of 'amount': {amount_sum}")
    print(f"  Sum of 'amount_company_currency': {company_sum}")
    
    # Show first 3 pending items
    for i, c in enumerate(pending[:3]):
        print(f"    Item {i+1}: amount={c.amount}, company_currency={c.amount_company_currency}, currency={c.currency.code}")
