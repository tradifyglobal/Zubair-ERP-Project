from accounting.models import Entity, UserEntity
from django.contrib.auth import get_user_model

User = get_user_model()

print("\n" + "="*80)
print("USER ENTITY ASSIGNMENTS CHECK")
print("="*80)

users = User.objects.all()
print(f"\nTotal Users: {users.count()}\n")

for user in users:
    print(f"\nUser: {user.username} (ID: {user.id})")
    print(f"Superuser: {user.is_superuser}")
    print(f"Staff: {user.is_staff}")
    
    # Check UserEntity assignments
    user_entities = UserEntity.objects.filter(user=user)
    print(f"Entity Assignments: {user_entities.count()}")
    
    if user_entities.exists():
        for ue in user_entities:
            print(f"  - {ue.entity.code}: {ue.entity.name} (Default: {ue.is_default}, Active: {ue.entity.is_active})")
    else:
        print("  NO ENTITY ASSIGNMENTS!")
        if user.is_superuser:
            print("  (But user is superuser - should have access to all)")

print("\n" + "="*80)
print("ALL ENTITIES")
print("="*80)

entities = Entity.objects.all()
print(f"\nTotal Entities: {entities.count()}\n")
for ent in entities:
    print(f"  - {ent.code}: {ent.name} (Active: {ent.is_active})")

print("\n" + "="*80)
print("SOLUTION")
print("="*80)
print("""
If a non-superuser has no UserEntity assignments, they cannot access any entity.

Fix options:
1. Make user a superuser (gets automatic access to all entities)
2. Create UserEntity records to assign user to specific entities

Current admin user needs UserEntity records created!
""")
