#!/usr/bin/env python
"""
Complete cleanup and reset script for TradifyERP
- Keeps only MAIN entity
- Deletes all other entities
- Deletes all contributions, shareholders, and accounts
- Keeps only one admin user
- Creates fresh INT-001 entity
"""

import os
import django
from django.db import connection
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from django.contrib.auth.models import User, Group
from accounting.models import (
    Entity, UserEntity, Account, LedgerEntry,
    CapitalContribution, Stakeholder, Currency
)

def backup_database():
    """Create a backup of the database"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_name = f'db_backup_before_cleanup_{timestamp}.sql'
    print(f"\n📦 Creating database backup: {backup_name}")
    os.system(f'pg_dump tradifyerp > /tmp/{backup_name}')
    print(f"✅ Backup created: /tmp/{backup_name}")
    return backup_name

def cleanup_contributions():
    """Delete all capital contributions"""
    print("\n🗑️  Deleting capital contributions...")
    count = CapitalContribution.objects.all().delete()[0]
    print(f"✅ Deleted {count} capital contributions")

def cleanup_stakeholders():
    """Delete all stakeholders"""
    print("\n🗑️  Deleting stakeholders...")
    count = Stakeholder.objects.all().delete()[0]
    print(f"✅ Deleted {count} stakeholders")

def cleanup_ledger_entries():
    """Delete all ledger entries"""
    print("\n🗑️  Deleting ledger entries...")
    count = LedgerEntry.objects.all().delete()[0]
    print(f"✅ Deleted {count} ledger entries")

def cleanup_accounts():
    """Delete all accounts"""
    print("\n🗑️  Deleting accounts...")
    count = Account.objects.all().delete()[0]
    print(f"✅ Deleted {count} accounts")

def cleanup_entities():
    """Delete all entities except MAIN"""
    print("\n🗑️  Deleting entities except MAIN...")
    entities_to_delete = Entity.objects.exclude(code='MAIN')
    count = 0
    for entity in entities_to_delete:
        print(f"  Deleting: {entity.code} - {entity.name}")
        entity.delete()
        count += 1
    print(f"✅ Deleted {count} entities")

def cleanup_users():
    """Keep only one admin user"""
    print("\n🗑️  Cleaning up users...")
    
    # Find or create admin user
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@tradifyerp.com',
            'first_name': 'Admin',
            'last_name': 'User',
            'is_staff': True,
            'is_superuser': True
        }
    )
    
    # Set password
    admin_user.set_password('admin123')
    admin_user.save()
    
    if created:
        print(f"✅ Created admin user: admin (password: admin123)")
    else:
        print(f"✅ Admin user already exists: admin (password reset to: admin123)")
    
    # Delete all other users except admin
    other_users = User.objects.exclude(username='admin')
    count = 0
    for user in other_users:
        print(f"  Deleting user: {user.username}")
        user.delete()
        count += 1
    
    print(f"✅ Deleted {count} other users")
    return admin_user

def cleanup_user_entities():
    """Delete all UserEntity assignments"""
    print("\n🗑️  Clearing UserEntity assignments...")
    count = UserEntity.objects.all().delete()[0]
    print(f"✅ Deleted {count} UserEntity assignments")

def setup_main_entity():
    """Setup MAIN entity with admin user"""
    print("\n✨ Setting up MAIN entity...")
    
    main_entity = Entity.objects.get(code='MAIN')
    admin_user = User.objects.get(username='admin')
    
    # Create UserEntity assignment
    user_entity, created = UserEntity.objects.get_or_create(
        user=admin_user,
        entity=main_entity,
        defaults={
            'is_default': True,
            'can_switch': True
        }
    )
    
    if created:
        print(f"✅ Assigned admin user to MAIN entity")
    else:
        print(f"✅ Admin user already assigned to MAIN entity")

def create_int001_entity():
    """Create fresh INT-001 entity"""
    print("\n✨ Creating INT-001 (Internal) entity...")
    
    try:
        # Get or create the entity
        entity, created = Entity.objects.get_or_create(
            code='INT-001',
            defaults={
                'name': 'Internal',
                'description': 'Internal - Headquarters',
                'is_active': True,
                'country': 'India',
                'company_currency': Currency.objects.first()  # Use first available currency
            }
        )
        
        if created:
            print(f"✅ Created entity: {entity.code} - {entity.name}")
        else:
            print(f"✅ Entity already exists: {entity.code} - {entity.name}")
        
        # Assign admin user to this entity
        admin_user = User.objects.get(username='admin')
        user_entity, created = UserEntity.objects.get_or_create(
            user=admin_user,
            entity=entity,
            defaults={
                'is_default': False,
                'can_switch': True
            }
        )
        
        if created:
            print(f"✅ Assigned admin user to INT-001 entity")
        
        return entity
    except Exception as e:
        print(f"❌ Error creating INT-001: {e}")
        return None

def create_capital_accounts(entity):
    """Create basic capital accounts for the entity"""
    print(f"\n✨ Creating accounts for {entity.code}...")
    
    try:
        # Create main capital account
        capital_main, created = Account.objects.get_or_create(
            entity=entity,
            account_number='3100',
            defaults={
                'name': 'Capital',
                'account_type': 'EQUITY',
                'is_active': True,
                'opening_balance': 0
            }
        )
        
        if created:
            print(f"  ✅ Created main account: {capital_main.account_number} - {capital_main.name}")
        
        # Create 8 shareholder sub-accounts
        shareholders = [
            'Mohammed Sanaullah',
            'Syed Atif Imran',
            'Mohammed Rafi',
            'Syed Safi',
            'Imteyazuddin Sameer Mohammed',
            'Fayazuddin Zubair Mohammed',
            'Nazrullah Shiekhmullah',
            'Arif Baba'
        ]
        
        for idx, shareholder in enumerate(shareholders, 1):
            account_num = f'3100-{idx:02d}'
            account, created = Account.objects.get_or_create(
                entity=entity,
                account_number=account_num,
                defaults={
                    'name': f'{shareholder} - Capital',
                    'account_type': 'EQUITY',
                    'parent_account': capital_main,
                    'is_active': True,
                    'opening_balance': 0
                }
            )
            
            if created:
                print(f"  ✅ Created sub-account: {account.account_number} - {account.name}")
        
        print(f"✅ Created {len(shareholders) + 1} accounts for {entity.code}")
        
    except Exception as e:
        print(f"❌ Error creating accounts: {e}")

def print_summary():
    """Print final summary"""
    print("\n" + "="*70)
    print("✅ CLEANUP AND SETUP COMPLETE")
    print("="*70)
    
    print("\n📊 System Status:")
    print(f"  Users: {User.objects.count()}")
    print(f"  Entities: {Entity.objects.count()}")
    print(f"  Total Accounts: {Account.objects.count()}")
    print(f"  UserEntity Assignments: {UserEntity.objects.count()}")
    print(f"  Stakeholders: {Stakeholder.objects.count()}")
    print(f"  Capital Contributions: {CapitalContribution.objects.count()}")
    print(f"  Ledger Entries: {LedgerEntry.objects.count()}")
    
    print("\n👤 Admin User:")
    admin = User.objects.get(username='admin')
    print(f"  Username: admin")
    print(f"  Email: {admin.email}")
    print(f"  Is Superuser: {admin.is_superuser}")
    
    print("\n🏢 Entities:")
    for entity in Entity.objects.all().order_by('code'):
        accounts = Account.objects.filter(entity=entity).count()
        print(f"  {entity.code:15} - {entity.name:30} ({accounts} accounts)")
    
    print("\n🔐 Login Credentials:")
    print("  Username: admin")
    print("  Password: admin123")
    
    print("\n" + "="*70)

def main():
    print("\n" + "="*70)
    print("🧹 TRADIFYERP COMPLETE CLEANUP AND RESET")
    print("="*70)
    
    # Confirm before proceeding
    confirm = input("\n⚠️  THIS WILL DELETE ALL DATA EXCEPT MAIN ENTITY!\nProceed? (yes/no): ")
    if confirm.lower() != 'yes':
        print("❌ Cleanup cancelled")
        return
    
    try:
        # Step 1: Backup
        backup_database()
        
        # Step 2: Cleanup in order
        cleanup_contributions()
        cleanup_stakeholders()
        cleanup_ledger_entries()
        cleanup_accounts()
        cleanup_entities()
        cleanup_user_entities()
        cleanup_users()
        
        # Step 3: Setup fresh data
        setup_main_entity()
        int001 = create_int001_entity()
        if int001:
            create_capital_accounts(int001)
        
        # Step 4: Summary
        print_summary()
        
        print("\n✨ System is ready! You can now log in with admin/admin123")
        
    except Exception as e:
        print(f"\n❌ Error during cleanup: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
