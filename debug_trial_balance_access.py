from accounting.models import Entity, UserEntity, LedgerEntry
from django.contrib.auth import get_user_model

User = get_user_model()

print("\n" + "="*80)
print("TRIAL BALANCE ACCESS DEBUG")
print("="*80)

# Check admin user
admin = User.objects.get(username='admin')
print(f"\nAdmin User: {admin.username}")
print(f"Superuser: {admin.is_superuser}")

# Check all entities admin has access to
admin_entities = UserEntity.objects.filter(user=admin)
print(f"\nAdmin Entity Assignments: {admin_entities.count()}")
for ue in admin_entities:
    print(f"  - {ue.entity.code}: {ue.entity.name} (Active: {ue.entity.is_active}, Default: {ue.is_default})")

# Check Test entity
test_entity = Entity.objects.get(code='Test')
print(f"\nTest Entity:")
print(f"  Code: {test_entity.code}")
print(f"  Name: {test_entity.name}")
print(f"  Active: {test_entity.is_active}")
print(f"  ID: {test_entity.id}")

# Check ledger entries for Test entity
entries = LedgerEntry.objects.filter(entity=test_entity)
print(f"\nLedger Entries in Test entity: {entries.count()}")

# Check if trial balance calculation works
print("\n" + "="*80)
print("TRIAL BALANCE CALCULATION TEST")
print("="*80)

try:
    from accounting.trial_balance import calculate_trial_balance
    from datetime import date
    
    tb_data = calculate_trial_balance(test_entity, date.today())
    
    if tb_data:
        print(f"\n✅ Trial Balance Calculation Successful!")
        print(f"Total Debits: {tb_data['total_debits']}")
        print(f"Total Credits: {tb_data['total_credits']}")
        print(f"Balanced: {tb_data['is_balanced']}")
        print(f"Accounts: {len(tb_data['account_balances'])}")
    else:
        print("\n❌ Trial Balance returned None")
        
except Exception as e:
    print(f"\n❌ Error calculating trial balance:")
    print(f"Error: {str(e)}")
    import traceback
    traceback.print_exc()

# Check for MAIN entity (admin's default)
main_entity = Entity.objects.get(code='MAIN')
print("\n" + "="*80)
print("MAIN Entity (Admin's Default)")
print("="*80)
print(f"Code: {main_entity.code}")
print(f"Name: {main_entity.name}")
print(f"Active: {main_entity.is_active}")
print(f"Ledger Entries: {LedgerEntry.objects.filter(entity=main_entity).count()}")

try:
    from accounting.trial_balance import calculate_trial_balance
    from datetime import date
    
    tb_data_main = calculate_trial_balance(main_entity, date.today())
    
    if tb_data_main:
        print(f"\n✅ MAIN Trial Balance works!")
        print(f"Total Debits: {tb_data_main['total_debits']}")
        print(f"Total Credits: {tb_data_main['total_credits']}")
    else:
        print("\n⚠️ MAIN entity has no trial balance data (no entries)")
        
except Exception as e:
    print(f"\n❌ Error with MAIN entity:")
    print(f"Error: {str(e)}")
