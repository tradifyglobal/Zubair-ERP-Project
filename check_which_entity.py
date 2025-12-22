from accounting.models import CapitalContribution

# List all contributions with 8000 on Oct 20 and their entities
contributions = CapitalContribution.objects.filter(
    amount=8000.00,
    contribution_date__month=10,
    contribution_date__day=20,
    contribution_date__year=2025
)

print(f'All 8000 CAD contributions from Oct 20, 2025:')
for cc in contributions:
    print(f'ID {cc.id}: {cc.entity.name} ({cc.entity.code}) - {cc.stakeholder} - Status: {cc.status}, Ledger: {cc.ledger_entry_id}')
