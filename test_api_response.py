#!/usr/bin/env python3
"""Test API endpoint to verify it returns grouped_accounts"""

import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from accounting.models import Account, Entity
from django.http import JsonResponse

# Get first entity
entity = Entity.objects.first()
if not entity:
    print("ERROR: No entity found")
    exit(1)

print(f"Entity: {entity.name} (ID: {entity.id})")
print("")

# Get main accounts
main_accounts = Account.objects.filter(
    entity=entity, 
    parent_account__isnull=True, 
    is_active=True
)[:3]

print(f"Total main accounts: {main_accounts.count()}")
print("")

for main in main_accounts:
    print(f"Main Account: {main.account_number} - {main.name}")
    
    # Get sub-accounts
    sub_accounts = Account.objects.filter(
        parent_account=main,
        entity=entity,
        is_active=True
    )
    
    print(f"  Sub-accounts: {sub_accounts.count()}")
    for sub in sub_accounts[:3]:
        print(f"    - {sub.account_number}: {sub.name}")
    print("")

# Now test the API response structure
print("\nTesting API Response Structure:")
print("=" * 60)

if main_accounts.exists():
    main = main_accounts.first()
    sub_accounts = Account.objects.filter(
        parent_account=main,
        entity=entity,
        is_active=True
    ).order_by('account_number')
    
    # Build response like the API does
    accounts_list = []
    grouped_accounts = {}
    
    has_sub_accounts = sub_accounts.exists()
    
    if has_sub_accounts:
        for account in sub_accounts:
            # Check if this account has sub-accounts
            has_children = account.sub_accounts.exists() if hasattr(account, 'sub_accounts') else False
            account_data = {
                'id': account.id,
                'account_number': account.account_number,
                'name': account.name,
                'account_type': account.account_type,
                'display_name': f"{account.account_number} - {account.name}",
                'has_children': has_children  # True if account has sub-accounts
            }
            accounts_list.append(account_data)
            
            parent_key = main.name
            if parent_key not in grouped_accounts:
                grouped_accounts[parent_key] = []
            grouped_accounts[parent_key].append(account_data)
    
    response = {
        'success': True,
        'main_account': {
            'id': main.id,
            'account_number': main.account_number,
            'name': main.name,
            'display_name': f"{main.account_number} - {main.name}"
        },
        'accounts': accounts_list,
        'grouped_accounts': grouped_accounts,
        'has_sub_accounts': has_sub_accounts,
        'count': len(accounts_list)
    }
    
    print(f"Main Account: {response['main_account']['display_name']}")
    print(f"Has Sub-Accounts: {response['has_sub_accounts']}")
    print(f"Sub-Account Count: {response['count']}")
    print(f"\nGrouped Accounts Structure:")
    print(json.dumps(response['grouped_accounts'], indent=2)[:500])
