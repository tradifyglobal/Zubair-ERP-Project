import os
import sys
sys.path.insert(0, 'G:\\TradifyERP')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')

import django
django.setup()

from accounting.models import Account, Stakeholder, Entity

print("=== Creating Shareholder Sub-Accounts ===\n")

# Get all entities
entities = Entity.objects.filter(is_active=True)

for entity in entities:
    print(f"Processing entity: {entity.name}")
    
    # Find all capital accounts for this entity
    capital_accounts = Account.objects.filter(
        entity=entity,
        account_type='EQUITY',
        is_active=True,
        parent_account__isnull=True  # Only parent accounts
    ).filter(name__icontains='capital')
    
    print(f"  Found {capital_accounts.count()} capital accounts")
    
    # Get all active stakeholders
    stakeholders = Stakeholder.objects.filter(entity=entity, status='ACTIVE')
    print(f"  Found {stakeholders.count()} active stakeholders")
    
    # Create sub-accounts for each stakeholder
    for capital_account in capital_accounts:
        print(f"\n  Capital Account: {capital_account.account_number} - {capital_account.name}")
        
        for stakeholder in stakeholders:
            sub_account = capital_account.get_shareholder_subaccount(stakeholder)
            if sub_account:
                print(f"    ✓ {sub_account.account_number} - {sub_account.name}")

print("\n=== Done! ===")
