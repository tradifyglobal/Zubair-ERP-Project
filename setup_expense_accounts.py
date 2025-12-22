#!/usr/bin/env python
"""
Setup Required GL Accounts for Expense Module
Creates necessary accounts for employee expense tracking with proper double-entry accounting

Accounts Created:
- 2100: Accounts Payable - Employee Expenses (LIABILITY)
- 5100: Travel Expense (EXPENSE)
- 5200: Office Supplies Expense (EXPENSE)
- 5300: Meals & Entertainment Expense (EXPENSE)
- 5400: Utilities Expense (EXPENSE)
- 5500: Maintenance & Repairs Expense (EXPENSE)

Run this once per entity before using the expense module.
"""

import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from django.db import transaction
from accounting.models import Entity, Account
from expenses.models import ExpenseCategory


def setup_expense_accounts(entity_code):
    """Setup expense accounts for a specific entity"""
    
    try:
        entity = Entity.objects.get(code=entity_code)
    except Entity.DoesNotExist:
        print(f"❌ Entity '{entity_code}' not found!")
        return False
    
    print(f"\n{'='*60}")
    print(f"Setting up Expense Accounts for Entity: {entity.name}")
    print(f"{'='*60}\n")
    
    accounts_config = [
        # LIABILITY ACCOUNTS
        {
            'account_number': '2100',
            'name': 'Accounts Payable - Employee Expenses',
            'account_type': 'LIABILITY',
            'description': 'Liability for approved employee expenses pending reimbursement',
            'is_header': False,
            'is_active': True,
        },
        
        # EXPENSE ACCOUNTS
        {
            'account_number': '5100',
            'name': 'Travel Expense',
            'account_type': 'EXPENSE',
            'description': 'Business travel costs including airfare, accommodation, transportation',
            'is_header': False,
            'is_active': True,
        },
        {
            'account_number': '5200',
            'name': 'Office Supplies Expense',
            'account_type': 'EXPENSE',
            'description': 'Office supplies, stationery, and equipment',
            'is_header': False,
            'is_active': True,
        },
        {
            'account_number': '5300',
            'name': 'Meals & Entertainment Expense',
            'account_type': 'EXPENSE',
            'description': 'Business meals and client entertainment',
            'is_header': False,
            'is_active': True,
        },
        {
            'account_number': '5400',
            'name': 'Utilities Expense',
            'account_type': 'EXPENSE',
            'description': 'Electricity, water, internet, phone bills',
            'is_header': False,
            'is_active': True,
        },
        {
            'account_number': '5500',
            'name': 'Maintenance & Repairs Expense',
            'account_type': 'EXPENSE',
            'description': 'Equipment and facility maintenance costs',
            'is_header': False,
            'is_active': True,
        },
        {
            'account_number': '5600',
            'name': 'Professional Services Expense',
            'account_type': 'EXPENSE',
            'description': 'Consulting, legal, accounting services',
            'is_header': False,
            'is_active': True,
        },
        {
            'account_number': '5700',
            'name': 'Training & Development Expense',
            'account_type': 'EXPENSE',
            'description': 'Employee training, courses, certifications',
            'is_header': False,
            'is_active': True,
        },
        {
            'account_number': '5800',
            'name': 'Communications Expense',
            'account_type': 'EXPENSE',
            'description': 'Telephone, internet, postage',
            'is_header': False,
            'is_active': True,
        },
    ]
    
    created_count = 0
    updated_count = 0
    
    with transaction.atomic():
        for acc_config in accounts_config:
            account, created = Account.objects.get_or_create(
                entity=entity,
                account_number=acc_config['account_number'],
                defaults={
                    'name': acc_config['name'],
                    'account_type': acc_config['account_type'],
                    'description': acc_config['description'],
                    'is_header': acc_config['is_header'],
                    'is_active': acc_config['is_active'],
                }
            )
            
            if created:
                print(f"✅ Created: {account.account_number} - {account.name} ({account.account_type})")
                created_count += 1
            else:
                # Update existing account
                account.name = acc_config['name']
                account.account_type = acc_config['account_type']
                account.description = acc_config['description']
                account.is_active = acc_config['is_active']
                account.save()
                print(f"🔄 Updated: {account.account_number} - {account.name} ({account.account_type})")
                updated_count += 1
    
    print(f"\n{'='*60}")
    print(f"✅ Accounts Setup Complete!")
    print(f"   Created: {created_count}")
    print(f"   Updated: {updated_count}")
    print(f"{'='*60}\n")
    
    return True


def setup_expense_categories(entity_code):
    """Setup default expense categories linked to GL accounts"""
    
    try:
        entity = Entity.objects.get(code=entity_code)
    except Entity.DoesNotExist:
        print(f"❌ Entity '{entity_code}' not found!")
        return False
    
    print(f"\n{'='*60}")
    print(f"Setting up Expense Categories for Entity: {entity.name}")
    print(f"{'='*60}\n")
    
    categories_config = [
        {
            'category_type': 'TRAVEL',
            'name': 'Travel Expenses',
            'account_number': '5100',
            'description': 'Business travel including flights, hotels, transportation',
            'requires_receipt': True,
            'requires_approval': True,
        },
        {
            'category_type': 'OFFICE_SUPPLIES',
            'name': 'Office Supplies',
            'account_number': '5200',
            'description': 'Stationery, printer supplies, office equipment',
            'requires_receipt': True,
            'requires_approval': False,
        },
        {
            'category_type': 'MEALS',
            'name': 'Meals & Entertainment',
            'account_number': '5300',
            'description': 'Business meals and client entertainment',
            'requires_receipt': True,
            'requires_approval': True,
        },
        {
            'category_type': 'UTILITIES',
            'name': 'Utilities',
            'account_number': '5400',
            'description': 'Electricity, water, internet bills',
            'requires_receipt': True,
            'requires_approval': True,
        },
        {
            'category_type': 'MAINTENANCE',
            'name': 'Maintenance & Repairs',
            'account_number': '5500',
            'description': 'Equipment and facility repairs',
            'requires_receipt': True,
            'requires_approval': True,
        },
        {
            'category_type': 'PROFESSIONAL_SERVICES',
            'name': 'Professional Services',
            'account_number': '5600',
            'description': 'Consulting, legal, accounting fees',
            'requires_receipt': True,
            'requires_approval': True,
        },
        {
            'category_type': 'TRAINING',
            'name': 'Training & Development',
            'account_number': '5700',
            'description': 'Employee training and certifications',
            'requires_receipt': True,
            'requires_approval': True,
        },
        {
            'category_type': 'COMMUNICATIONS',
            'name': 'Communications',
            'account_number': '5800',
            'description': 'Phone, internet, postage',
            'requires_receipt': True,
            'requires_approval': False,
        },
    ]
    
    created_count = 0
    updated_count = 0
    
    with transaction.atomic():
        for cat_config in categories_config:
            # Get the GL account
            try:
                expense_account = Account.objects.get(
                    entity=entity,
                    account_number=cat_config['account_number']
                )
            except Account.DoesNotExist:
                print(f"❌ Account {cat_config['account_number']} not found! Run setup_expense_accounts first.")
                continue
            
            category, created = ExpenseCategory.objects.get_or_create(
                entity=entity,
                category_type=cat_config['category_type'],
                defaults={
                    'name': cat_config['name'],
                    'description': cat_config['description'],
                    'expense_account': expense_account,
                    'requires_receipt': cat_config['requires_receipt'],
                    'requires_approval': cat_config['requires_approval'],
                    'is_active': True,
                }
            )
            
            if created:
                print(f"✅ Created: {category.name} → Account {expense_account.account_number}")
                created_count += 1
            else:
                # Update existing category
                category.name = cat_config['name']
                category.description = cat_config['description']
                category.expense_account = expense_account
                category.requires_receipt = cat_config['requires_receipt']
                category.requires_approval = cat_config['requires_approval']
                category.save()
                print(f"🔄 Updated: {category.name} → Account {expense_account.account_number}")
                updated_count += 1
    
    print(f"\n{'='*60}")
    print(f"✅ Categories Setup Complete!")
    print(f"   Created: {created_count}")
    print(f"   Updated: {updated_count}")
    print(f"{'='*60}\n")
    
    return True


def main():
    """Main setup function"""
    print("\n" + "="*60)
    print(" EXPENSE MODULE GL ACCOUNT SETUP")
    print("="*60)
    
    # Get all active entities
    entities = Entity.objects.filter(is_active=True)
    
    if not entities.exists():
        print("❌ No active entities found!")
        return
    
    print(f"\nFound {entities.count()} active entity(ies):\n")
    for i, entity in enumerate(entities, 1):
        print(f"{i}. {entity.code} - {entity.name}")
    
    print("\nOptions:")
    print("  - Enter entity code (e.g., 'ENT001')")
    print("  - Enter 'all' to setup for all entities")
    print("  - Enter 'quit' to exit")
    
    choice = input("\nYour choice: ").strip()
    
    if choice.lower() == 'quit':
        print("Cancelled.")
        return
    
    if choice.lower() == 'all':
        for entity in entities:
            setup_expense_accounts(entity.code)
            setup_expense_categories(entity.code)
    else:
        setup_expense_accounts(choice)
        setup_expense_categories(choice)
    
    print("\n✅ All setup complete!")
    print("\nNext steps:")
    print("1. Verify accounts in Admin: /admin/accounting/account/")
    print("2. Verify categories in Admin: /admin/expenses/expensecategory/")
    print("3. Test expense workflow: Create → Approve → Reimburse")
    print("4. Check GL entries: /admin/accounting/ledgerentry/\n")


if __name__ == '__main__':
    main()
