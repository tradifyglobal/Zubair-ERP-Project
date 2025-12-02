"""
Ensure all superusers and staff members are assigned to appropriate entities
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from django.contrib.auth.models import User
from accounting.models import UserEntity, Entity

print("\n" + "="*80)
print("VERIFYING AND FIXING ALL ADMIN USER ENTITY ASSIGNMENTS")
print("="*80 + "\n")

# Get all admin/staff users
admin_users = User.objects.filter(is_staff=True) | User.objects.filter(is_superuser=True)
admin_users = admin_users.distinct()

print(f"Total Admin/Staff Users: {admin_users.count()}")

# Get all active entities
entities = Entity.objects.filter(is_active=True)
print(f"Total Active Entities: {entities.count()}\n")

# Ensure all admin users are assigned to all entities
for admin in admin_users:
    current_entities = UserEntity.objects.filter(user=admin).count()
    print(f"{admin.username} (ID: {admin.id}):")
    print(f"  Currently assigned to: {current_entities} entities")
    
    missing_assignments = 0
    for idx, entity in enumerate(entities):
        ue, created = UserEntity.objects.get_or_create(
            user=admin,
            entity=entity,
            defaults={
                'is_default': (idx == 0),  # First entity is default
                'can_switch': True
            }
        )
        if created:
            missing_assignments += 1
    
    if missing_assignments > 0:
        print(f"  ✓ Added {missing_assignments} missing entity assignments")
    
    final_count = UserEntity.objects.filter(user=admin).count()
    print(f"  Now assigned to: {final_count} entities\n")

print("="*80)
print("\nRun diagnostic again to verify all users now show in dashboard:")
print("  python diagnose_user_dashboard_issue.py")
print("="*80 + "\n")
