#!/usr/bin/env python
import os, sys, django
sys.path.insert(0, '/var/www/tradifyerp')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings_production')
django.setup()

from accounting.models import CapitalContribution, Entity

# Get Testing entity
entity = Entity.objects.get(id=7)

print('='*80)
print('DASHBOARD VERIFICATION FOR TESTING ENTITY')
print('='*80)

# Verify the exact dashboard query
dashboard_contributions = CapitalContribution.objects.filter(
    entity_id=entity.id,
    workflow_status='APPROVED'
).order_by('-contribution_date')

print(f'\nQuery: CapitalContribution.objects.filter(entity_id={entity.id}, workflow_status="APPROVED")')
print(f'Result Count: {dashboard_contributions.count()}')

if dashboard_contributions.exists():
    print('\n✓ Contributions found for dashboard display:')
    for cc in dashboard_contributions:
        print(f'\n  #{cc.id}: {cc.stakeholder.full_name}')
        print(f'    Amount: {cc.amount_company_currency} {cc.currency_destination.code}')
        print(f'    Date: {cc.contribution_date}')
        print(f'    Status: {cc.status}')
        print(f'    Workflow: {cc.workflow_status}')
else:
    print('\n✗ No approved contributions found for dashboard!')

# Also check shareholder page query
print('\n' + '='*80)
print('SHAREHOLDER CONTRIBUTION PAGE QUERY')
print('='*80)

for stakeholder in entity.stakeholders.all()[:5]:
    stakeholder_contribs = CapitalContribution.objects.filter(
        entity=entity,
        stakeholder=stakeholder,
        workflow_status='APPROVED'
    )
    if stakeholder_contribs.exists():
        total = sum(cc.amount_company_currency or cc.amount for cc in stakeholder_contribs)
        print(f'\n{stakeholder.full_name}:')
        print(f'  Contributions: {stakeholder_contribs.count()}')
        print(f'  Total: {total}')
        for cc in stakeholder_contribs:
            print(f'    - {cc.amount_company_currency} {cc.currency_destination.code} on {cc.contribution_date}')
