from accounting.models import CapitalContribution, Account

# Get contribution 24
cc = CapitalContribution.objects.get(id=24)
entity = cc.entity

print(f'Entity: {entity.name} ({entity.code})')
print(f'Total Accounts in entity: {Account.objects.filter(entity=entity).count()}')

# Check by type
for acc_type in ['ASSET', 'LIABILITY', 'EQUITY', 'REVENUE', 'EXPENSE']:
    count = Account.objects.filter(entity=entity, account_type=acc_type).count()
    print(f'{acc_type}: {count}')
    if count > 0:
        accs = Account.objects.filter(entity=entity, account_type=acc_type)[:3]
        for acc in accs:
            print(f'  - {acc.account_number}: {acc.name}')

