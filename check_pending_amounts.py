#!/usr/bin/env python3
"""Check pending amounts in the database"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from django.db.models import Sum
from accounting.models import CapitalContribution, Entity

# Get INT-001 entity
entity = Entity.objects.filter(name='INT-001').first()
if not entity:
    entity = Entity.objects.all().first()

if entity:
    pending = CapitalContribution.objects.filter(entity=entity, status='PENDING')
    print(f"Entity: {entity.name}")
    print(f"Pending contributions count: {pending.count()}")
    
    # Get both totals
    total_amount = pending.aggregate(total=Sum('amount'))['total']
    total_company = pending.aggregate(total=Sum('amount_company_currency'))['total']
    
    print(f"Total amount (source currency): {total_amount}")
    print(f"Total amount_company_currency: {total_company}")
    
    # Show individual items
    print("\nIndividual pending contributions:")
    for contrib in pending.values('id', 'amount', 'amount_company_currency', 'currency__code'):
        print(f"  ID {contrib['id']}: {contrib['amount']} {contrib['currency__code']} -> ₹{contrib['amount_company_currency']}")
else:
    print("No entity found!")
