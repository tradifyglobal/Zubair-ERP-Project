from accounting.models import Entity, Account, CapitalContribution
from django.db import transaction

# Get INT-005 entity
entity = Entity.objects.get(code='INT-005')
print(f'Setting up hierarchical chart of accounts for {entity.name} ({entity.code})')

# Get currency
currency = entity.company_currency or entity.currency_destination
if not currency:
    from accounting.models import Currency
    currency = Currency.objects.first()

print(f'Using currency: {currency.code}\n')

# Create or get main Capital account
main_capital, created = Account.objects.get_or_create(
    entity=entity,
    account_number='3100',
    defaults={
        'name': 'Capital',
        'account_type': 'EQUITY',
        'currency': currency,
        'description': 'Main capital contributions account',
        'parent_account': None
    }
)
print(f'Main Capital Account: {main_capital.account_number} ({main_capital.name}) - {"created" if created else "exists"}')

# Get all unique stakeholders with contributions in this entity
stakeholders = CapitalContribution.objects.filter(entity=entity).values_list('stakeholder', flat=True).distinct()
stakeholders_objs = []
for sh_id in stakeholders:
    from accounting.stakeholder_models import Stakeholder
    try:
        sh = Stakeholder.objects.get(id=sh_id)
        stakeholders_objs.append(sh)
    except:
        pass

print(f'\nFound {len(stakeholders_objs)} unique stakeholders')

# Create sub-accounts for each shareholder
sub_account_num = 1
for stakeholder in stakeholders_objs:
    sub_account_code = f'3100-{str(sub_account_num).zfill(2)}'
    sub_account_name = f'{stakeholder.full_name}'
    
    sub_account, created = Account.objects.get_or_create(
        entity=entity,
        account_number=sub_account_code,
        defaults={
            'name': sub_account_name,
            'account_type': 'EQUITY',
            'currency': currency,
            'description': f'Capital account for {sub_account_name}',
            'parent_account': main_capital
        }
    )
    
    status = "created" if created else "exists"
    print(f'  {sub_account.account_number}: {sub_account.name} - {status}')
    
    sub_account_num += 1

print(f'\n✓ Hierarchical chart of accounts setup complete!')
