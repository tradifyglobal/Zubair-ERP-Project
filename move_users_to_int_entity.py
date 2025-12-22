#!/usr/bin/env python
"""
Script to move all users from tradify entity to int entity
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from accounting.models import Entity, UserEntity
from django.contrib.auth.models import User

# Get entities
tradify_entity = Entity.objects.filter(code='TRADIFY').first()
int_entity = Entity.objects.filter(code='INT-001').first()

print(f"Tradify Entity: {tradify_entity}")
print(f"Int Entity: {int_entity}")

if not tradify_entity or not int_entity:
    print("Error: One or both entities not found!")
    exit(1)

# Get all users assigned to tradify entity
tradify_users = UserEntity.objects.filter(entity=tradify_entity)
print(f"\nTotal users in 'tradify' entity: {tradify_users.count()}")

# List users
for ue in tradify_users:
    print(f"  - {ue.user.username} ({ue.user.get_full_name()})")

# Move users
print(f"\nMoving users from '{tradify_entity.name}' to '{int_entity.name}'...")
count = 0
for ue in tradify_users:
    # Get the user
    user = ue.user
    
    # Check if user already has assignment in int entity
    existing_int_assignment = UserEntity.objects.filter(user=user, entity=int_entity).first()
    
    if existing_int_assignment:
        # Update existing assignment to make it default
        existing_int_assignment.is_default = True
        existing_int_assignment.save()
        print(f"  ✓ Updated {user.username} (already in INT-001)")
    else:
        # Create new assignment
        UserEntity.objects.create(
            user=user,
            entity=int_entity,
            is_default=True,
            can_switch=ue.can_switch
        )
        print(f"  ✓ Moved {user.username}")
    
    # Delete old TRADIFY assignment
    ue.delete()
    count += 1

print(f"\n✓ Successfully moved {count} users to '{int_entity.name}' entity")

# Verify
remaining_tradify = UserEntity.objects.filter(entity=tradify_entity).count()
new_int_users = UserEntity.objects.filter(entity=int_entity).count()
print(f"\nVerification:")
print(f"  Users in 'tradify' entity now: {remaining_tradify}")
print(f"  Users in 'int' entity now: {new_int_users}")
