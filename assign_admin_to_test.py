from accounting.models import Entity, UserEntity
from django.contrib.auth import get_user_model

User = get_user_model()

# Get admin user
admin = User.objects.get(username='admin')
print(f"Admin user: {admin.username} (Superuser: {admin.is_superuser})")

# Get Test entity
test_entity = Entity.objects.get(code='Test')
print(f"Test entity: {test_entity.code} - {test_entity.name}")

# Check if UserEntity already exists
existing = UserEntity.objects.filter(user=admin, entity=test_entity).first()

if existing:
    print(f"\nUserEntity already exists:")
    print(f"  Default: {existing.is_default}")
else:
    # Create UserEntity for admin -> Test
    user_entity = UserEntity.objects.create(
        user=admin,
        entity=test_entity,
        is_default=False,  # Keep MAIN as default
        can_switch=True
    )
    print(f"\n✅ Created UserEntity:")
    print(f"  User: {admin.username}")
    print(f"  Entity: {test_entity.code} - {test_entity.name}")
    print(f"  Default: False")

print("\n" + "="*80)
print("ADMIN USER ENTITY ASSIGNMENTS")
print("="*80)

admin_entities = UserEntity.objects.filter(user=admin)
for ue in admin_entities:
    default_marker = " (DEFAULT)" if ue.is_default else ""
    print(f"  - {ue.entity.code}: {ue.entity.name}{default_marker}")

print("\n✅ Admin can now access both MAIN and Test entities!")
print("Go to: https://tradifyglobal.com/accounting/select-entity/")
print("Select 'Test - Testing' to see all your data!")
