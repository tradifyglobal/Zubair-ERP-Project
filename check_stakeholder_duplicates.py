#!/usr/bin/env python
"""Check why stakeholder IDs don't match"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings_production')
sys.path.insert(0, '/var/www/tradifyerp')
django.setup()

from accounting.models import Stakeholder, Entity

# Search for "Mohammed Rafi" across all entities
rafi_records = Stakeholder.objects.filter(first_name='Mohammed', last_name='Rafi')
print(f"Found {rafi_records.count()} 'Mohammed Rafi' records:")
for rafi in rafi_records:
    print(f"  - ID: {rafi.id}, Entity: {rafi.entity.name if rafi.entity else 'NO ENTITY'}, Email: {rafi.email}")

print("\n" + "=" * 80 + "\n")

# Search for "Syed Safi"
safi_records = Stakeholder.objects.filter(first_name='Syed', last_name='Safi')
print(f"Found {safi_records.count()} 'Syed Safi' records:")
for safi in safi_records:
    print(f"  - ID: {safi.id}, Entity: {safi.entity.name if safi.entity else 'NO ENTITY'}, Email: {safi.email}")

print("\n" + "=" * 80 + "\n")

# Search for "Mohammed Sanaullah"
sanaullah_records = Stakeholder.objects.filter(first_name='Mohammed', last_name='Sanaullah')
print(f"Found {sanaullah_records.count()} 'Mohammed Sanaullah' records:")
for sanaullah in sanaullah_records:
    print(f"  - ID: {sanaullah.id}, Entity: {sanaullah.entity.name if sanaullah.entity else 'NO ENTITY'}, Email: {sanaullah.email}")

print("\n" + "=" * 80 + "\n")

# Check the entities
print("All entities:")
for entity in Entity.objects.all():
    count = Stakeholder.objects.filter(entity=entity).count()
    print(f"  - {entity.name} (ID: {entity.id}): {count} stakeholders")
