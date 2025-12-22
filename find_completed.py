from accounting.models import CapitalContribution, LedgerEntry

# Find contributions with 8000 that are COMPLETED
completed = CapitalContribution.objects.filter(
    amount=8000.00,
    status='COMPLETED',
    contribution_date__month=10,
    contribution_date__day=20,
    contribution_date__year=2025
)

print(f'Completed contributions with 8000 on Oct 20:  {completed.count()}')
for cc in completed:
    print(f'ID {cc.id}: {cc.stakeholder}, Status: {cc.status}, Workflow: {cc.workflow_status}, Ledger: {cc.ledger_entry_id}')
    entries = LedgerEntry.objects.filter(reference_number=f'CAP-{cc.id}')
    print(f'  Ledger entries: {entries.count()}')
