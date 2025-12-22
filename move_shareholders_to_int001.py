#!/usr/bin/env python
"""
Script to move all shareholders from TRADIFY entity to INT-001 entity
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from accounting.models import Entity, Stakeholder

# Get the entities
tradify = Entity.objects.filter(code='TRADIFY').first()
int_001 = Entity.objects.filter(code='INT-001').first()

if not tradify:
    print("❌ TRADIFY entity not found")
    exit(1)

if not int_001:
    print("❌ INT-001 entity not found")
    exit(1)

# Get shareholders from TRADIFY entity
shareholders = Stakeholder.objects.filter(entity=tradify)
count = shareholders.count()

print(f"Found {count} shareholders in TRADIFY entity:")
for s in shareholders:
    print(f"  - {s.first_name} {s.last_name}")

if count > 0:
    print(f"\nMoving {count} shareholders from {tradify.code} to {int_001.code}...")
    for s in shareholders:
        s.entity = int_001
        s.save()
        print(f"  ✓ Moved: {s.first_name} {s.last_name}")
    print(f"\n✓ Successfully moved {count} shareholders to {int_001.code}")
else:
    print("\nNo shareholders to move")
