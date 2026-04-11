#!/usr/bin/env python3
"""
Check Ahsan's contribution amounts to see why total_invested is wrong
"""

import os
import django
import sys
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
sys.path.insert(0, '/var/www/tradifyerp')
django.setup()

from accounting.models import CapitalContribution, Entity, Stakeholder

entity = Entity.objects.filter(name__icontains='Pristine').first()
ahsan = Stakeholder.objects.filter(entity=entity, first_name__icontains='Ahsan').first()

print(f"Entity: {entity.name}")
print(f"Stakeholder: {ahsan.full_name}")
print("=" * 80)

# Get all Ahsan's COMPLETED contributions
completed = CapitalContribution.objects.filter(
    stakeholder=ahsan,
    status='COMPLETED'
).order_by('-amount_company_currency')

print(f"\nAhsan's COMPLETED Contributions:")
print("-" * 80)

total_company = Decimal('0')
total_usd = Decimal('0')

for contrib in completed:
    amount_company = Decimal(str(contrib.amount_company_currency or 0))
    amount_usd = Decimal(str(contrib.amount_usd or 0))
    
    total_company += amount_company
    total_usd += amount_usd
    
    print(f"Amount Company: ₹{amount_company:>12,.2f}")
    print(f"Amount USD:     ${amount_usd:>12,.2f}")
    print(f"Exchange Rate:  {contrib.exchange_rate}")
    print()

print(f"Total (Company Currency): ₹{total_company:,.2f}")
print(f"Total (USD):              ${total_usd:,.2f}")

print(f"\nProperty Values:")
print(f"  stakeholder.total_invested = ${ahsan.total_invested:,.2f}")

# Debug: Check what the property is actually summing
print(f"\nDebug - Property Filter Query:")
contrib_for_property = ahsan.capital_contributions.filter(status='COMPLETED')
print(f"  Count: {contrib_for_property.count()}")

prop_total = Decimal('0')
for c in contrib_for_property:
    print(f"    - {c.amount_company_currency:>10,.2f} (USD: {c.amount_usd:>10,.2f})")
    prop_total += Decimal(str(c.amount_usd or 0))

print(f"  Sum of amount_usd: ${prop_total:,.2f}")

print(f"\nIssue Analysis:")
print(f"Expected total: ₹700,000.00 (all 5 completed)")
print(f"Property shows: ${ahsan.total_invested:,.2f} (seems to be missing 1 contribution)")
