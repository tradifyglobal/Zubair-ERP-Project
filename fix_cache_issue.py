#!/usr/bin/env python3
"""
Fix the stakeholder.total_invested property by refreshing from DB
"""

import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
sys.path.insert(0, '/var/www/tradifyerp')
django.setup()

from accounting.models import Stakeholder, Entity
from django.core.cache import cache

entity = Entity.objects.filter(name__icontains='Pristine').first()
ahsan_id = 136  # The stakeholder ID from the URL

# Clear all Django caches
cache.clear()

print(f"Clearing Django caches...")
print("=" * 80)

# Reload the Stakeholder from database (forces fresh query)
ahsan = Stakeholder.objects.get(id=ahsan_id)

print(f"Stakeholder: {ahsan.full_name}")
print(f"  ID: {ahsan.id}")

# Get total_invested - this will recalculate from the database
total_invested = ahsan.total_invested

print(f"\nAfter cache clear and DB reload:")
print(f"  stakeholder.total_invested = ${total_invested:,.2f}")

# Verify by manual sum
from decimal import Decimal
completed = ahsan.capital_contributions.filter(status='COMPLETED')
manual_sum = sum(Decimal(str(c.amount_usd or 0)) for c in completed)

print(f"\nVerification:")
print(f"  Manual sum of amount_usd = ${manual_sum:,.2f}")
print(f"  Property value          = ${total_invested:,.2f}")

if float(total_invested) == float(manual_sum):
    print(f"\n✓ Property is now correct!")
else:
    print(f"\n⚠️  Values still don't match - there may be a deeper issue")
    print(f"   Difference: {float(manual_sum) - float(total_invested)}")

print(f"\nContext implications:")
print(f"  - Template will show: ${total_invested:,.2f}")
print(f"  - View shows Completed Contributions: ₹700,000.00")
print(f"  - These should match when converted to same currency")
