#!/usr/bin/env python3

import os
import sys
import django

sys.path.append('/var/www/tradifyerp')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from accounting.models import Entity

def activate_entities():
    print("=== ACTIVATING ENTITIES ===")
    
    # Show current entity status
    entities = Entity.objects.all().order_by('id')
    print("Current entity status:")
    for entity in entities:
        print(f"  {entity.code} - {entity.name} (ID: {entity.id}): Active = {entity.is_active}")
    
    # Activate Internal entity (INT-001)
    try:
        internal_entity = Entity.objects.get(name="Internal")
        internal_entity.is_active = True
        internal_entity.save()
        print(f"\n✓ Activated: {internal_entity.code} - {internal_entity.name}")
    except Entity.DoesNotExist:
        print("\n✗ Internal entity not found")
    
    # Activate Main Company entity (MAIN)
    try:
        main_entity = Entity.objects.get(name="Main Company")
        main_entity.is_active = True
        main_entity.save()
        print(f"✓ Activated: {main_entity.code} - {main_entity.name}")
    except Entity.DoesNotExist:
        print("✗ Main Company entity not found")
    
    # Show updated entity status
    print(f"\nUpdated entity status:")
    entities = Entity.objects.all().order_by('id')
    active_count = 0
    for entity in entities:
        status = "✓ ACTIVE" if entity.is_active else "✗ inactive"
        print(f"  {entity.code} - {entity.name}: {status}")
        if entity.is_active:
            active_count += 1
    
    print(f"\nTotal active entities: {active_count}")
    print("Users can now select between active entities in their session.")

if __name__ == '__main__':
    activate_entities()
    print("\n=== DONE ===")