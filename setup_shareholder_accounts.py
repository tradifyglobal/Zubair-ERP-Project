#!/usr/bin/env python
"""
Create hierarchical chart of accounts for INT-001.
Setup: 3100 Capital with 20 shareholder sub-accounts (3100-01 to 3100-20)
"""

from decimal import Decimal
from django.db import transaction
from accounting.models import Entity, Account, Currency, Stakeholder

print("\n" + "="*70)
print("HIERARCHICAL CHART OF ACCOUNTS SETUP - INT-001")
print("="*70)

try:
    entity = Entity.objects.get(code='INT-005')
    print(f"\n✓ Entity: {entity.name} ({entity.code})")
    
    currency = entity.company_currency or Currency.objects.get(code='INR')
    print(f"✓ Currency: {currency.code}")
    
    # Get all unique shareholders from the system
    all_stakeholders = Stakeholder.objects.filter(
        capital_contributions__entity=entity
    ).distinct().order_by('id')
    
    total_stakeholders = all_stakeholders.count()
    print(f"✓ Total shareholders in INT-001: {total_stakeholders}")
    print(f"✓ Creating accounts for: {min(20, total_stakeholders)} shareholders\n")
    
    # Step 1: Create or get main Capital account (3100)
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
            'parent_account': None,
        }
    )
    
    status = "✓ CREATED" if created else "✓ EXISTS"
    print(f"Main Account:")
    print(f"  {status} | 3100 - Capital")
    
    # Step 2: Create sub-accounts for each shareholder (up to 20)
    print(f"\nShareholder Sub-Accounts:")
    created_count = 0
    
    for idx, stakeholder in enumerate(all_stakeholders[:20], 1):
        sub_account_code = f'3100-{idx:02d}'
        
        # Get shareholder name
        if stakeholder.stakeholder_type == 'INDIVIDUAL':
            shareholder_name = stakeholder.full_name
        else:
            shareholder_name = stakeholder.company_name or str(stakeholder)
        
        # Create or get sub-account
        sub_account, created = Account.objects.get_or_create(
            entity=entity,
            account_number=sub_account_code,
            defaults={
                'name': f"{shareholder_name}",
                'account_type': 'EQUITY',
                'description': f"Capital account for {shareholder_name}",
                'currency': currency,
                'opening_balance': Decimal('0.00'),
                'is_active': True,
                'parent_account': main_capital,
            }
        )
        
        status = "✓ NEW" if created else "  EXISTS"
        print(f"  {status} | {sub_account_code} - {shareholder_name}")
        if created:
            created_count += 1
    
    # Summary
    total_accounts = Account.objects.filter(
        entity=entity, 
        account_number__startswith='3100'
    ).count()
    
    print("\n" + "="*70)
    print(f"✓ Created: {created_count} new shareholder accounts")
    print(f"✓ Total Capital Accounts (3100*): {total_accounts}")
    print("="*70 + "\n")
    
except Exception as e:
    print(f"\n✗ ERROR: {type(e).__name__}: {e}\n")
    import traceback
    traceback.print_exc()
