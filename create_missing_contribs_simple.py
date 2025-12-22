#!/usr/bin/env python
import os, sys, django
sys.path.insert(0, '/var/www/tradifyerp')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings_production')
django.setup()

from accounting.models import CapitalContribution, Stakeholder, Entity, Currency
from datetime import date

# Get Testing entity
entity = Entity.objects.get(id=7)  # Use ID to be sure

print('='*80)
print('CREATING MISSING CAPITAL CONTRIBUTION RECORDS FOR TESTING ENTITY')
print('='*80)

# Get default currency for this entity
try:
    # Most companies use INR or USD - check what's available
    default_currency = Currency.objects.filter(code='INR').first()
    if not default_currency:
        default_currency = Currency.objects.filter(code='USD').first()
    if not default_currency:
        default_currency = Currency.objects.first()
    
    if not default_currency:
        print('ERROR: No currency found in database!')
        sys.exit(1)
    
    print(f'Using currency: {default_currency.code} ({default_currency.name})')
except Exception as e:
    print(f'ERROR getting currency: {e}')
    sys.exit(1)

# List all stakeholders
all_stakeholders = Stakeholder.objects.filter(entity=entity)
print(f'\nAll stakeholders in {entity.name} (ID: {entity.id}):')
for s in all_stakeholders:
    print(f'  ID={s.id}: {s.full_name} ({s.stakeholder_type})')

# Find stakeholders by first_name (Fayaz, Imtey)
print('\n' + '='*80)
print('SEARCHING FOR SPECIFIC STAKEHOLDERS')
print('='*80)

fayaz = Stakeholder.objects.filter(entity=entity, first_name__icontains='Fayaz').first()
imtey = Stakeholder.objects.filter(entity=entity, first_name__icontains='Imtey').first()

if fayaz:
    print(f'\n✓ Found Fayazuddin: ID={fayaz.id}, Name={fayaz.full_name}')
else:
    print('\n✗ Fayazuddin not found - trying other searches...')
    # Try other search patterns
    all_by_name = Stakeholder.objects.filter(entity=entity)
    for s in all_by_name:
        if s.first_name and ('Fayaz' in s.first_name or 'Fayaz' in (s.last_name or '')):
            print(f'  Found: {s.full_name} (ID={s.id})')
            fayaz = s
            break

if imtey:
    print(f'✓ Found Imteyazuddin: ID={imtey.id}, Name={imtey.full_name}')
else:
    print('✗ Imteyazuddin not found - trying other searches...')
    # Try other search patterns
    all_by_name = Stakeholder.objects.filter(entity=entity)
    for s in all_by_name:
        if s.first_name and ('Imtey' in s.first_name or 'Imtey' in (s.last_name or '')):
            print(f'  Found: {s.full_name} (ID={s.id})')
            imtey = s
            break

# Create contributions if stakeholders found
if fayaz and imtey:
    print('\n' + '='*80)
    print('CREATING CAPITAL CONTRIBUTION RECORDS')
    print('='*80)
    
# Create contributions if stakeholders found
if fayaz and imtey:
    print('\n' + '='*80)
    print('CREATING CAPITAL CONTRIBUTION RECORDS')
    print('='*80)
    
    # Create contribution for Fayazuddin
    cc1 = CapitalContribution.objects.create(
        entity=entity,
        stakeholder=fayaz,
        contribution_date=date.today(),
        amount=4000.00,
        currency=default_currency,
        currency_destination=default_currency,
        status='COMPLETED',
        workflow_status='APPROVED',
        payment_mode='CASH',
        is_auto_posted=False
    )
    print(f'\n✓ Created CapitalContribution #{cc1.id} for {fayaz.full_name}')
    print(f'  Amount: {cc1.amount} {default_currency.code}')
    print(f'  Status: {cc1.status}')
    print(f'  Workflow: {cc1.workflow_status}')
    
    # Create contribution for Imteyazuddin
    cc2 = CapitalContribution.objects.create(
        entity=entity,
        stakeholder=imtey,
        contribution_date=date.today(),
        amount=5000.00,
        currency=default_currency,
        currency_destination=default_currency,
        status='COMPLETED',
        workflow_status='APPROVED',
        payment_mode='CASH',
        is_auto_posted=False
    )
    print(f'\n✓ Created CapitalContribution #{cc2.id} for {imtey.full_name}')
    print(f'  Amount: {cc2.amount} {default_currency.code}')
    print(f'  Status: {cc2.status}')
    print(f'  Workflow: {cc2.workflow_status}')
    
    # Verify they appear in dashboard query
    print('\n' + '='*80)
    print('VERIFICATION')
    print('='*80)
    
    approved_contribs = CapitalContribution.objects.filter(
        entity=entity,
        workflow_status='APPROVED'
    )
    print(f'\nTotal APPROVED contributions in Testing entity: {approved_contribs.count()}')
    for cc in approved_contribs:
        print(f'  #{cc.id}: {cc.stakeholder.full_name} - {cc.amount}')
    
    print('\n✓ SUCCESS: Contributions created and ready for dashboard display!')
    
else:
    print('\n✗ ERROR: Could not find one or both stakeholders')
    if not fayaz:
        print('  - Fayazuddin not found')
    if not imtey:
        print('  - Imteyazuddin not found')
    print('\nAvailable first_name values:')
    for s in Stakeholder.objects.filter(entity=entity):
        print(f'  - {s.first_name} {s.last_name} (ID={s.id})')
