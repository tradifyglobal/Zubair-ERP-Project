#!/usr/bin/env python3
"""Test API endpoint"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings_production')
django.setup()

from accounting.models import Account, Entity
import requests

def main():
    entity = Entity.objects.first()
    cash_account = Account.objects.filter(entity=entity, account_number='100001').first()
    
    if cash_account:
        print(f'Cash Account ID: {cash_account.id}')
        print(f'Entity ID: {entity.id}')
        
        # Test the API endpoint
        url = f'http://localhost:8000/accounting/api/get-sub-accounts/?main_account_id={cash_account.id}&entity_id={entity.id}'
        
        try:
            response = requests.get(url)
            data = response.json()
            print(f'\n=== API Response ===')
            print(f'Success: {data.get("success")}')
            print(f'Main Account Fallback: {data.get("main_account_fallback")}')
            print(f'Sub-accounts count: {len(data.get("sub_accounts", []))}')
            
            if data.get('sub_accounts'):
                for acc in data['sub_accounts']:
                    print(f'  - {acc["account_number"]} - {acc["name"]} (ID: {acc["id"]})')
        except Exception as e:
            print(f'Error testing API: {e}')
    else:
        print('Cash account not found')

if __name__ == '__main__':
    main()