import os, sys, django
sys.path.insert(0, '/var/www/tradifyerp')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings_production')
django.setup()

from accounting.models import CapitalContribution, CashReceiptLine, BankReceiptLine, Entity, LedgerEntry

# Get Testing entity
test_entity = Entity.objects.filter(name__in=['Test', 'Testing']).first()
print('='*80)
print('INVESTIGATING CAPITAL CONTRIBUTION IN TEST ENTITY')
print('='*80)

print('\nAvailable Entities:')
for e in Entity.objects.all():
    print(f'  {e.name} (ID: {e.id})')

if test_entity:
    print(f'\nEntity: {test_entity.name} (ID: {test_entity.id})')
    
    print('\n1. CAPITAL CONTRIBUTIONS IN TEST ENTITY:')
    contribs = CapitalContribution.objects.filter(entity=test_entity).order_by('-id')
    print(f'   Count: {contribs.count()}')
    if contribs.exists():
        for cc in contribs[:3]:
            print(f'\n   ID: {cc.id}')
            print(f'   Stakeholder: {cc.stakeholder}')
            print(f'   Amount: {cc.amount_company_currency or cc.amount}')
            print(f'   Status: {cc.status}')
            print(f'   Workflow: {cc.workflow_status}')
            print(f'   Auto-posted: {cc.is_auto_posted}')
            print(f'   Source Receipt: cash={cc.source_cash_receipt_id}, bank={cc.source_bank_receipt_id}')
    
    print('\n2. CASH RECEIPTS WITH STAKEHOLDER IN TEST ENTITY:')
    receipts = CashReceiptLine.objects.filter(entity=test_entity, stakeholder__isnull=False).order_by('-id')
    print(f'   Count: {receipts.count()}')
    for r in receipts[:3]:
        print(f'   ID: {r.id}, Stakeholder: {r.stakeholder}, Workflow: {r.workflow_status}, Posted: {r.is_capital_contribution_posted}')
    
    print('\n2b. ALL CASH RECEIPTS IN TEST ENTITY:')
    all_receipts = CashReceiptLine.objects.filter(entity=test_entity).order_by('-id')
    print(f'   Count: {all_receipts.count()}')
    for r in all_receipts[:5]:
        print(f'   ID: {r.id}, Stakeholder: {r.stakeholder}, Workflow: {r.workflow_status}, Amount: {r.debit_amount}')
    
    print('\n3. GL ENTRIES FOR TEST ENTITY:')
    gl_entries = LedgerEntry.objects.filter(account__entity=test_entity).order_by('-created_at')[:10]
    print(f'   Recent GL Entries: {gl_entries.count()}')
    for ge in gl_entries[:5]:
        account = ge.account
        print(f'   {ge.created_at.date()}: {account.name} ({account.account_number}) {ge.entry_type}:{ge.amount}')
        # Check if this account belongs to a stakeholder
        if 'Capital' in account.name:
            print(f'      -> Account name contains "Capital"')
    
    print('\n4. DASHBOARD VIEW QUERY:')
    entity_id = test_entity.id
    from django.db.models import Sum, Q
    dashboard_contribs = CapitalContribution.objects.filter(
        entity_id=entity_id,
        workflow_status='APPROVED'
    )
    print(f'   APPROVED contributions in Test: {dashboard_contribs.count()}')
    for cc in dashboard_contribs:
        print(f'     {cc.id}: {cc.stakeholder} - {cc.amount_company_currency or cc.amount}')

else:
    print('Test entity not found')
