from accounting.models import CapitalContribution, LedgerEntry

# Get contribution 23 specifically (Imteyazuddin Sameer Mohammed from Oct 20)
cc = CapitalContribution.objects.get(id=23)

print(f'Contribution 23 Details:')
print(f'Stakeholder: {cc.stakeholder}')
print(f'Amount Company Currency: {cc.amount_company_currency}')
print(f'Status: {cc.status}')
print(f'Workflow Status: {cc.workflow_status}')
print(f'Ledger Entry ID: {cc.ledger_entry_id}')
print(f'Ledger Entry Object: {cc.ledger_entry}')
print(f'Equity Account: {cc.equity_account}')
print(f'Cash Account: {cc.cash_account}')

# Try to find any ledger entries
entries = LedgerEntry.objects.filter(reference_number='CAP-23')
print(f'\nLedger entries for CAP-23: {entries.count()}')
for entry in entries:
    print(f'  ID {entry.id}: {entry.entry_type} {entry.amount} to {entry.account.name}')

# Check if there are any ledger entries at all related to this contribution
print(f'\nAll ledger entries in the entity:')
all_entries = LedgerEntry.objects.filter(entity=cc.entity).count()
print(f'Total: {all_entries}')




