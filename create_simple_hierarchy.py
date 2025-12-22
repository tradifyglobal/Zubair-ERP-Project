#!/usr/bin/env python
"""
Create simple hierarchical chart of accounts for INT-005.
Create 3100 (Capital) with 15 direct sub-accounts for shareholders.
NO nested hierarchies - just 2 levels.
"""

from decimal import Decimal
from django.db import transaction
from accounting.models import Entity, Account, Currency, CapitalContribution, Stakeholder

print("\n" + "="*60)
print("Creating Simple Hierarchical Accounts")
print("="*60)

entity = Entity.objects.get(entity_code='INT-005')
print(f"\nEntity: {entity.name} ({entity.entity_code})")

currency = entity.company_currency or Currency.objects.get(code='INR')
print(f"Currency: {currency.code}")

# Step 1: Create or get main Capital account
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
        'parent_account': None,  # Top level
    }
)

status = "CREATED" if created else "EXISTS"
print(f"\n✓ Main Capital Account: 3100 - {main_capital.name} [{status}]")

# Step 2: Get unique stakeholders from completed contributions
stakeholders = Stakeholder.objects.filter(
    capitalcontribution__entity=entity,
    capitalcontribution__workflow_status='COMPLETED'
).distinct().order_by('id')

print(f"\nFound {stakeholders.count()} unique stakeholders with completed contributions")

if not stakeholders.exists():
    print("ERROR: No stakeholders found!")
    exit(1)

# Step 3: Create sub-accounts - SIMPLE 2-LEVEL ONLY
print(f"\nCreating sub-accounts (3100-01 through 3100-{stakeholders.count():02d})...")
created_count = 0

for idx, stakeholder in enumerate(stakeholders, 1):
    sub_account_code = f'3100-{str(idx).zfill(2)}'
    
    if stakeholder.stakeholder_type == 'INDIVIDUAL':
        shareholder_name = stakeholder.full_name
    else:
        shareholder_name = stakeholder.company_name or str(stakeholder)
    
    sub_account, created = Account.objects.get_or_create(
        entity=entity,
        account_number=sub_account_code,
        defaults={
            'name': f"{shareholder_name} - Capital",
            'account_type': 'EQUITY',
            'description': f"Capital account for {shareholder_name}",
            'currency': currency,
            'opening_balance': Decimal('0.00'),
            'is_active': True,
            'parent_account': main_capital,  # Direct child of 3100
        }
    )
    
    if created:
        print(f"  ✓ {sub_account_code} - {shareholder_name}")
        created_count += 1

print(f"\n{'='*60}")
print(f"✓ Successfully created {created_count} sub-accounts")
print(f"✓ Total capital accounts: {Account.objects.filter(entity=entity, account_number__startswith='3100').count()}")
print(f"{'='*60}\n")
