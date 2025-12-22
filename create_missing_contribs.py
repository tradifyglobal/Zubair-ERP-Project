import os, sys, django
sys.path.insert(0, '/var/www/tradifyerp')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings_production')
django.setup()

from accounting.models import CapitalContribution, Stakeholder, Entity
from datetime import date

# Get Testing entity
entity = Entity.objects.get(name='Testing')

print('='*80)
print('CREATING MISSING CAPITAL CONTRIBUTION RECORDS')
print('='*80)

# First, find all stakeholders in Testing entity
all_stakeholders = Stakeholder.objects.filter(entity=entity)
print(f'\nAll stakeholders in {entity.name}:')
for s in all_stakeholders:
    print(f'  {s.id}: {s.full_name} (type: {s.stakeholder_type})')

# Get stakeholders by name
# Note: full_name is a property, so we filter by first_name instead
fayaz = Stakeholder.objects.filter(entity=entity, first_name__icontains='Fayaz').first()
imtey = Stakeholder.objects.filter(entity=entity, first_name__icontains='Imtey').first()

print(f'\nSearching for stakeholders...')
print(f'Fayazuddin: {fayaz}')
print(f'Imteyazuddin: {imtey}')

if fayaz and imtey:
    # Create contribution for Fayazuddin
    cc1 = CapitalContribution.objects.create(
        entity=entity,
        stakeholder=fayaz,
        contribution_date=date.today(),
        amount=4000.00,
        status='COMPLETED',
        workflow_status='APPROVED',
        payment_mode='CASH',
        is_auto_posted=False  # Manually created
    )
    print(f'\nCreated contribution for {fayaz}:')
    print(f'  ID: {cc1.id}')
    print(f'  Amount: 4000.00')
    print(f'  Status: APPROVED')
    
    # Create contribution for Imteyazuddin
    cc2 = CapitalContribution.objects.create(
        entity=entity,
        stakeholder=imtey,
        contribution_date=date.today(),
        amount=5000.00,
        status='COMPLETED',
        workflow_status='APPROVED',
        payment_mode='CASH',
        is_auto_posted=False  # Manually created
    )
    print(f'\nCreated contribution for {imtey}:')
    print(f'  ID: {cc2.id}')
    print(f'  Amount: 5000.00')
    print(f'  Status: APPROVED')
    
    # Verify they appear in dashboard query
    approved_contribs = CapitalContribution.objects.filter(
        entity=entity,
        workflow_status='APPROVED'
    )
    print(f'\nTotal APPROVED contributions in Testing entity: {approved_contribs.count()}')
    for cc in approved_contribs:
        print(f'  {cc.id}: {cc.stakeholder} - {cc.amount}')
    
else:
    print('ERROR: Could not find stakeholders')
