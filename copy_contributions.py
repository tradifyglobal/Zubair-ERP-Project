#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
os.chdir('/var/www/tradifyerp')
django.setup()

from accounting.models import Entity, CapitalContribution

# Find entities
internal = Entity.objects.get(code='INT-005')
testing = Entity.objects.get(code='testing-001')

print('Copying from: ' + internal.name + ' to ' + testing.name)

# Get contributions from internal entity
contributions = CapitalContribution.objects.filter(entity=internal)
print('Total contributions to copy: ' + str(contributions.count()))

copied_count = 0
for contrib in contributions:
    # Create a copy with the new entity - make reference unique
    ref_num = (contrib.reference_number or 'COPY-') + '-' + str(contrib.id)
    new_contrib = CapitalContribution(
        entity=testing,
        stakeholder=contrib.stakeholder,
        contribution_date=contrib.contribution_date,
        amount=contrib.amount,
        currency=contrib.currency,
        currency_destination=contrib.currency_destination,
        exchange_rate=contrib.exchange_rate,
        amount_usd=contrib.amount_usd,
        amount_company_currency=contrib.amount_company_currency,
        payment_mode=contrib.payment_mode,
        reference_number=ref_num,
        status=contrib.status,
        workflow_status='DRAFT'
    )
    new_contrib.save()
    copied_count += 1
    print('Copied: ' + contrib.stakeholder.full_name + ' - ' + str(contrib.amount_company_currency))

print('\nTotal copied: ' + str(copied_count))
