#!/usr/bin/env python3
"""Check cash account structure"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings_production')
django.setup()

from accounting.models import Account, Entity

def main():
    entity = Entity.objects.first()
    print('=== CASH ACCOUNT STRUCTURE ===')
    
    # Check main cash account
    cash_account = Account.objects.filter(entity=entity, account_number='100001').first()
    if cash_account:
        print(f'Main Account: {cash_account.account_number} - {cash_account.name}')
        print(f'Has Parent: {cash_account.parent_account}')
        print(f'Is Active: {cash_account.is_active}')
        
        # Check sub-accounts
        sub_accounts = Account.objects.filter(
            entity=entity, 
            parent_account=cash_account, 
            is_active=True
        ).order_by('account_number')
        
        print(f'Sub-accounts count: {sub_accounts.count()}')
        for sub in sub_accounts:
            print(f'  Sub: {sub.account_number} - {sub.name}')
    else:
        print('Cash account 100001 not found')
    
    print('\n=== ALL CASH-RELATED ACCOUNTS (1000x) ===')
    cash_accounts = Account.objects.filter(
        entity=entity, 
        account_number__startswith='1000'
    ).order_by('account_number')
    
    for acc in cash_accounts:
        parent_info = f" (Parent: {acc.parent_account.account_number})" if acc.parent_account else " (No Parent)"
        print(f'{acc.account_number} - {acc.name}{parent_info}')
    
    print('\n=== FORM FIELD REQUIREMENTS ===')
    # Check if the form requires sub-account selection for 100001
    if cash_account:
        if sub_accounts.exists():
            print('✓ Sub-accounts available - form should allow selection')
        else:
            print('✗ NO sub-accounts available - this causes the form error!')
            print('   Either create sub-accounts or make field optional')

if __name__ == '__main__':
    main()