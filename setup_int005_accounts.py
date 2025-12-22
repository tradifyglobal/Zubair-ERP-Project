from accounting.models import Entity, CapitalContribution, LedgerEntry

# Get INT-005 entity
entity = Entity.objects.get(code='INT-005')
print(f'Checking ledger entries in {entity.name} ({entity.code})')

# Check all contributions in INT-005
contributions = CapitalContribution.objects.filter(entity=entity)
print(f'\nAll contributions in {entity.name}:')
for cc in contributions:
    print(f'ID {cc.id}: {cc.stakeholder} - {cc.amount_company_currency} - Status: {cc.status} - Ledger: {cc.ledger_entry_id}')

# Check ledger entries
entries = LedgerEntry.objects.filter(entity=entity)
print(f'\nTotal ledger entries in {entity.name}: {entries.count()}')
for entry in entries:
    print(f'ID {entry.id}: {entry.entry_type} {entry.amount} to {entry.account.name}')





