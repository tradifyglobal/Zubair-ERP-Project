"""
Fix: Assign Admin user to all entities so they can manage users across the system
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from django.contrib.auth.models import User
from accounting.models import UserEntity, Entity

print("\n" + "="*80)
print("FIXING ADMIN USER ENTITY ASSIGNMENT")
print("="*80 + "\n")

# Get admin user
try:
    admin_user = User.objects.get(id=2, username='Admin')
    print(f"Found Admin user: {admin_user.username} (ID: {admin_user.id})")
except User.DoesNotExist:
    print("ERROR: Admin user not found!")
    exit(1)

# Get all active entities
entities = Entity.objects.filter(is_active=True)
print(f"\nActive Entities: {entities.count()}")

# Check current assignments
current_assignments = UserEntity.objects.filter(user=admin_user)
print(f"Current Entity Assignments: {current_assignments.count()}")

if current_assignments.exists():
    print("  Current assignments:")
    for ue in current_assignments:
        print(f"    - {ue.entity.name} (ID: {ue.entity.id}) {'[DEFAULT]' if ue.is_default else ''}")

# Assign admin to all entities
print(f"\nAssigning Admin to all {entities.count()} active entities...")
for i, entity in enumerate(entities, 1):
    ue, created = UserEntity.objects.get_or_create(
        user=admin_user,
        entity=entity,
        defaults={
            'is_default': (i == 1),  # First entity is default
            'can_switch': True
        }
    )
    if created:
        print(f"  ✓ Created: {entity.name} {'(DEFAULT)' if ue.is_default else ''}")
    else:
        print(f"  → Already exists: {entity.name}")

print(f"\nAdmin user now has access to {UserEntity.objects.filter(user=admin_user).count()} entities!")
print("\n" + "="*80 + "\n")
