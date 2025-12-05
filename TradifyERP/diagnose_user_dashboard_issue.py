"""
Diagnostic script to identify why user changes don't show in dashboard/admin
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from django.contrib.auth.models import User
from accounting.models import UserEntity, Entity
from django.db.models import Q

print("\n" + "="*80)
print("USER DASHBOARD VISIBILITY DIAGNOSTIC")
print("="*80 + "\n")

# Get all entities
entities = Entity.objects.all()
print(f"Total Entities: {entities.count()}")
for e in entities:
    print(f"  - {e.id}: {e.name} ({e.code})")

# Get all users
all_users = User.objects.all()
print(f"\n Total Users in System: {all_users.count()}")

# Check user-entity relationships
print(f"\nUserEntity Assignments:")
user_entity_count = UserEntity.objects.count()
print(f"  Total UserEntity records: {user_entity_count}")

# Find users NOT assigned to any entity
unassigned_users = User.objects.exclude(
    id__in=UserEntity.objects.values_list('user_id', flat=True)
).all()

if unassigned_users.exists():
    print(f"\n⚠️  WARNING: {unassigned_users.count()} users NOT assigned to any entity:")
    for user in unassigned_users:
        print(f"    - {user.username} (ID: {user.id}) - Status: {'Active' if user.is_active else 'Inactive'}")
        print(f"      → These users will NOT show in any entity's user list!")
else:
    print(f"\n✓ All {all_users.count()} users are assigned to at least one entity")

# Show user distribution by entity
print(f"\nUser Distribution by Entity:")
for entity in entities:
    entity_users = User.objects.filter(
        id__in=UserEntity.objects.filter(entity=entity).values_list('user_id', flat=True)
    )
    print(f"\n  Entity: {entity.name} (ID: {entity.id})")
    print(f"    Total users: {entity_users.count()}")
    for user in entity_users[:5]:  # Show first 5
        user_entities = UserEntity.objects.filter(user=user)
        is_default = "DEFAULT" if user_entities.filter(is_default=True, entity=entity).exists() else ""
        print(f"      - {user.username} (ID: {user.id}) {is_default}")
    if entity_users.count() > 5:
        print(f"      ... and {entity_users.count() - 5} more")

# Check for recently created users
from django.utils import timezone
from datetime import timedelta

recent_date = timezone.now() - timedelta(days=1)
recent_users = User.objects.filter(date_joined__gte=recent_date)
print(f"\nRecently Created Users (last 24 hours): {recent_users.count()}")
for user in recent_users:
    user_entities = UserEntity.objects.filter(user=user)
    print(f"  - {user.username} (ID: {user.id})")
    print(f"    Created: {user.date_joined}")
    print(f"    Assigned to {user_entities.count()} entities:")
    for ue in user_entities:
        print(f"      • {ue.entity.name} {'(DEFAULT)' if ue.is_default else ''}")

print("\n" + "="*80)
print("DIAGNOSIS SUMMARY")
print("="*80)
print("""
If users are not showing in the dashboard/admin after creation or editing:

1. ✓ Check if users are assigned to the current session entity
   → UserListView filters by: selected_entity_id from session
   → Users must be in UserEntity table for current entity to appear

2. ✓ Check if browser is caching the page
   → Clear browser cache (Ctrl+Shift+Delete)
   → Try Ctrl+F5 for hard refresh
   → We've added cache-control headers to prevent this

3. ✓ Check if Django is caching templates
   → Already cleared by migrations and server restart

4. ✓ Check if static files need to be collected
   → Run: python manage.py collectstatic --noinput

5. ✓ Check if changes were actually saved to database
   → Query the database directly (see above)

Recommended Actions:
- Clear all browser caches
- Hard refresh browser (Ctrl+F5)
- Clear Django cache if using Redis/Memcached
- Verify user is assigned to current entity in UserEntity table
""")
print("="*80 + "\n")
