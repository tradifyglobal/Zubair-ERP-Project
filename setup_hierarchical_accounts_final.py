"""
Setup hierarchical chart of accounts with sub-accounts for each shareholder.
This script creates a 3100 Capital main account with sub-accounts for each shareholder.
"""

from decimal import Decimal
from django.db import transaction
from accounting.models import Entity, Account, Currency, CapitalContribution, Stakeholder

@transaction.atomic
def setup_hierarchical_accounts():
    # Get the Internal (INT-005) entity
    entity = Entity.objects.get(entity_code='INT-005')
    print(f"\nSetting up hierarchical chart of accounts for {entity.name} ({entity.entity_code})")
    
    # Get or create currency
    currency = entity.company_currency or Currency.objects.get(code='INR')
    print(f"Using currency: {currency.code}")
    
    # Get all unique stakeholders from completed capital contributions
    stakeholders = Stakeholder.objects.filter(
        capitalcontribution__entity=entity,
        capitalcontribution__workflow_status='COMPLETED'
    ).distinct().order_by('id')
    
    print(f"\nFound {stakeholders.count()} unique stakeholders")
    
    if not stakeholders.exists():
        print("No stakeholders with completed contributions found.")
        return
    
    # Create or get the main 3100 Capital account
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
        status = "created" if created else "exists"
        print(f"\n✓ Main Capital Account: {main_capital.account_number} ({main_capital.name}) - {status}")
    except Exception as e:
        print(f"\n✗ Error creating main capital account: {e}")
        return
    
    # Create sub-accounts for each stakeholder
    created_count = 0
    sub_account_num = 1
    
    print(f"\nCreating sub-accounts for {stakeholders.count()} stakeholders...")
    
    for stakeholder in stakeholders:
        try:
            # Generate shareholder-specific sub-account
            sub_account_code = f'3100-{str(sub_account_num).zfill(2)}'
            
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
                    'parent_account': main_capital,
                }
            )
            
            if created:
                print(f"  ✓ {sub_account_code} - {shareholder_name}")
                created_count += 1
            
            sub_account_num += 1
            
        except Exception as e:
            print(f"  ✗ Error creating sub-account for {stakeholder}: {e}")
    
    print(f"\n✓ Successfully created {created_count} sub-accounts")
    print("\nHierarchical account structure ready for use!")

if __name__ == '__main__':
    setup_hierarchical_accounts()
