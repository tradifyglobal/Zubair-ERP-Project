from decimal import Decimal
from django.db import transaction
from accounting.models import Entity, Account, Currency, CapitalContribution, Stakeholder

print("\nCreating Simple Hierarchical Accounts for INT-005")
print("="*60)

try:
    entity = Entity.objects.get(code='INT-001')
    print(f"✓ Entity: {entity.name}")
    
    currency = entity.company_currency or Currency.objects.get(code='INR')
    print(f"✓ Currency: {currency.code}")
    
    # Create/get main account
    main_capital, created = Account.objects.get_or_create(
        entity=entity,
        account_number='3100',
        defaults={
            'name': 'Capital',
            'account_type': 'EQUITY',
            'currency': currency,
            'opening_balance': Decimal('0.00'),
            'is_active': True,
        }
    )
    print(f"✓ Main Account 3100: {'CREATED' if created else 'EXISTS'}")
    
    # Get stakeholders with ANY contribution (not just completed)
    stakeholders = Stakeholder.objects.filter(
        capital_contributions__entity=entity
    ).distinct().order_by('id')
    
    print(f"✓ Found {stakeholders.count()} stakeholders")
    
    created_count = 0
    for idx, sh in enumerate(stakeholders, 1):
        name = sh.full_name if sh.stakeholder_type == 'INDIVIDUAL' else (sh.company_name or str(sh))
        sub_acct, created = Account.objects.get_or_create(
            entity=entity,
            account_number=f'3100-{idx:02d}',
            defaults={
                'name': f"{name} - Capital",
                'account_type': 'EQUITY',
                'currency': currency,
                'opening_balance': Decimal('0.00'),
                'is_active': True,
                'parent_account': main_capital,
            }
        )
        if created:
            created_count += 1
    
    total = Account.objects.filter(entity=entity, account_number__startswith='3100').count()
    print(f"✓ Created {created_count} sub-accounts")
    print(f"✓ Total 3100 accounts: {total}")
    print("="*60)

except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
