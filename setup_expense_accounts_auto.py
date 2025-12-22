#!/usr/bin/env python
"""
Automated Setup for Expense Module GL Accounts
Runs setup for all active entities without user interaction
"""

import os
import sys
import django

# Setup Django environment
sys.path.append('/var/www/tradifyerp')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings_production')
django.setup()

from django.db import transaction
from accounting.models import Entity, Account
from expenses.models import ExpenseCategory


def setup_expense_accounts(entity):
    """Setup expense accounts for a specific entity"""
    
    print(f"\n{'='*60}")
    print(f"Setting up Expense Accounts for Entity: {entity.name}")
    print(f"{'='*60}\n")
    
    # Get entity's currency
    currency = entity.company_currency
    
    accounts_config = [
        # LIABILITY ACCOUNTS
        {
            'account_number': '2100',
            'name': 'Accounts Payable - Employee Expenses',
            'account_type': 'LIABILITY',
            'description': 'Liability for approved employee expenses pending reimbursement',
            'is_active': True,
        },
        
        # EXPENSE ACCOUNTS
        {
            'account_number': '5100',
            'name': 'Travel Expense',
            'account_type': 'EXPENSE',
            'description': 'Business travel costs including airfare, accommodation, transportation',
            'is_active': True,
        },
        {
            'account_number': '5200',
            'name': 'Office Supplies Expense',
            'account_type': 'EXPENSE',
            'description': 'Office supplies, stationery, and equipment',
            'is_active': True,
        },
        {
            'account_number': '5300',
            'name': 'Meals & Entertainment Expense',
            'account_type': 'EXPENSE',
            'description': 'Business meals and client entertainment',
            'is_active': True,
        },
        {
            'account_number': '5400',
            'name': 'Utilities Expense',
            'account_type': 'EXPENSE',
            'description': 'Electricity, water, internet, phone bills',
            'is_active': True,
        },
        {
            'account_number': '5500',
            'name': 'Maintenance & Repairs Expense',
            'account_type': 'EXPENSE',
            'description': 'Equipment and facility maintenance costs',
            'is_active': True,
        },
        {
            'account_number': '5600',
            'name': 'Professional Services Expense',
            'account_type': 'EXPENSE',
            'description': 'Consulting, legal, accounting services',
            'is_active': True,
        },
        {
            'account_number': '5700',
            'name': 'Training & Development Expense',
            'account_type': 'EXPENSE',
            'description': 'Employee training, courses, certifications',
            'is_active': True,
        },
        {
            'account_number': '5800',
            'name': 'Communications Expense',
            'account_type': 'EXPENSE',
            'description': 'Telephone, internet, postage',
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
                    'is_active': acc_config['is_active'],
                    'currency': currency,
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
    
    print(f"\n   Created: {created_count}, Updated: {updated_count}")
    return created_count + updated_count


def setup_expense_categories(entity):
    """Setup default expense categories linked to GL accounts"""
    
    print(f"\nSetting up Expense Categories for Entity: {entity.name}\n")
    
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
                print(f"❌ Account {cat_config['account_number']} not found! Skipping {cat_config['name']}")
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
    
    print(f"\n   Created: {created_count}, Updated: {updated_count}")
    return created_count + updated_count


def main():
    """Main setup function - runs automatically for all entities"""
    print("\n" + "="*60)
    print(" EXPENSE MODULE GL ACCOUNT SETUP - AUTOMATED")
    print("="*60)
    
    # Get all active entities
    entities = Entity.objects.filter(is_active=True)
    
    if not entities.exists():
        print("❌ No active entities found!")
        return
    
    print(f"\nFound {entities.count()} active entity(ies)\n")
    
    total_accounts = 0
    total_categories = 0
    
    for entity in entities:
        total_accounts += setup_expense_accounts(entity)
        total_categories += setup_expense_categories(entity)
    
    print(f"\n{'='*60}")
    print(f"✅ ALL SETUP COMPLETE!")
    print(f"   Total Accounts: {total_accounts}")
    print(f"   Total Categories: {total_categories}")
    print(f"{'='*60}\n")
    
    print("Next steps:")
    print("1. Verify accounts: https://tradifyglobal.com/admin/accounting/account/")
    print("2. Verify categories: https://tradifyglobal.com/admin/expenses/expensecategory/")
    print("3. Restart Gunicorn: sudo systemctl restart gunicorn")
    print("4. Test expense workflow\n")


if __name__ == '__main__':
    main()
