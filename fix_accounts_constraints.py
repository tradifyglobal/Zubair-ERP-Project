"""
Fix the Account model constraint and create hierarchical accounts
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from decimal import Decimal
from django.db import transaction, connection
from accounting.models import Entity, Account, Currency, Stakeholder

def check_constraint():
    """Check the current state of the Account model"""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT constraint_name, constraint_type 
            FROM information_schema.table_constraints 
            WHERE table_name = 'accounting_account'
            AND constraint_type = 'UNIQUE'
        """)
        constraints = cursor.fetchall()
    
    print("\nCurrent UNIQUE constraints on accounting_account:")
    for constraint in constraints:
        print(f"  - {constraint[0]} ({constraint[1]})")
    
    return constraints

def remove_unique_constraint():
    """Remove the global unique constraint on account_number"""
    try:
        with connection.cursor() as cursor:
            # Try to drop the unique constraint
            cursor.execute("ALTER TABLE accounting_account DROP CONSTRAINT accounting_account_account_number_key")
        print("\n✓ Dropped global unique constraint on account_number")
        return True
    except Exception as e:
        print(f"\n✗ Could not drop constraint: {e}")
        return False

@transaction.atomic
def setup_hierarchical_accounts():
    """Create hierarchical account structure"""
    # Get the Internal (INT-005) entity
    try:
        entity = Entity.objects.get(entity_code='INT-005')
    except Entity.DoesNotExist:
        print("Entity INT-005 not found")
        return
    
    print(f"\nSetting up hierarchical chart of accounts for {entity.name}")
    
    # Get or create currency
    currency = entity.company_currency or Currency.objects.get(code='INR')
    print(f"Using currency: {currency.code}")
    
    # Get all unique stakeholders from completed capital contributions
    stakeholders = Stakeholder.objects.filter(
        capitalcontribution__entity=entity,
        capitalcontribution__workflow_status='COMPLETED'
    ).distinct().order_by('id')
    
    print(f"Found {stakeholders.count()} unique stakeholders")
    
    if not stakeholders.exists():
        print("No stakeholders found")
        return
    
    # Create or get main capital account
    try:
        main_capital, created = Account.objects.get_or_create(
            entity=entity,
            account_number='3100',
            defaults={
                'name': 'Capital',
                'account_type': 'EQUITY',
                'description': 'Shareholder Capital Accounts',
                'currency': currency,
                'opening_balance': Decimal('0.00'),
                'is_active': True,
            }
        )
        print(f"✓ Main Capital: {main_capital.account_number} ({main_capital.name})")
    except Exception as e:
        print(f"✗ Error creating main capital: {e}")
        return
    
    # Create sub-accounts
    created_count = 0
    for idx, stakeholder in enumerate(stakeholders, 1):
        try:
            sub_account_code = f'3100-{str(idx).zfill(2)}'
            
            if stakeholder.stakeholder_type == 'INDIVIDUAL':
                name = stakeholder.full_name
            else:
                name = stakeholder.company_name or str(stakeholder)
            
            sub_account, created = Account.objects.get_or_create(
                entity=entity,
                account_number=sub_account_code,
                defaults={
                    'name': f"{name} - Capital",
                    'account_type': 'EQUITY',
                    'description': f"Capital account for {name}",
                    'currency': currency,
                    'opening_balance': Decimal('0.00'),
                    'is_active': True,
                    'parent_account': main_capital,
                }
            )
            
            if created:
                print(f"  ✓ Created {sub_account_code}")
                created_count += 1
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    print(f"\n✓ Created {created_count} sub-accounts")

if __name__ == '__main__':
    print("=" * 60)
    print("Account Model Constraint Fix & Hierarchical Setup")
    print("=" * 60)
    
    # Check current constraints
    check_constraint()
    
    # Remove unique constraint
    remove_unique_constraint()
    
    # Verify it's gone
    check_constraint()
    
    # Setup hierarchical accounts
    print("\n" + "=" * 60)
    setup_hierarchical_accounts()
    print("\n" + "=" * 60)
