#!/usr/bin/env python3

import os
import sys
import django

# Add the project directory to the Python path
sys.path.append('/var/www/tradifyerp')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from accounting.models import CashPaymentLine, CapitalContribution, LedgerEntry, Account, Stakeholder

print("=== ANALYZING WHY CP001 ISN'T IN CAPITAL CONTRIBUTIONS ===")

# Get the cash payment
cp001 = CashPaymentLine.objects.filter(reference_number='CP001').first()
print(f"Cash Payment CP001:")
print(f"  Account: {cp001.account}")
print(f"  Credit Account: {cp001.credit_account}")
print(f"  Amount: {cp001.debit_amount}")
print(f"  Status: {cp001.workflow_status}")
print()

# Check if there should be a capital contribution
capital_account = cp001.account
print(f"Capital Account Details:")
print(f"  Number: {capital_account.account_number}")
print(f"  Name: {capital_account.name}")
print(f"  Type: {capital_account.account_type}")
print()

# Check for matching stakeholder
stakeholders = Stakeholder.objects.filter(entity=cp001.entity)
print(f"Available Stakeholders in {cp001.entity}:")
for stakeholder in stakeholders:
    print(f"  {stakeholder.id}: {stakeholder.full_name}")
print()

# Check if there's a matching capital contribution
contributions = CapitalContribution.objects.filter(
    entity=cp001.entity,
    amount=cp001.debit_amount
)
print(f"Matching Capital Contributions (amount {cp001.debit_amount}):")
for contrib in contributions:
    print(f"  {contrib.id}: {contrib.stakeholder} - {contrib.amount} - {contrib.status}")
print()

# Check capital contributions by stakeholder name
stakeholder_name = capital_account.name.replace(' - Capital', '')
print(f"Looking for stakeholder with name: '{stakeholder_name}'")

matching_stakeholders = Stakeholder.objects.filter(
    entity=cp001.entity
).filter(
    first_name__icontains='Fayazuddin'
)
print(f"Matching stakeholders: {matching_stakeholders.count()}")
for s in matching_stakeholders:
    full_name = f"{s.first_name} {s.middle_name or ''} {s.last_name}".strip()
    print(f"  {s.id}: {full_name}")

if matching_stakeholders.exists():
    stakeholder = matching_stakeholders.first()
    stakeholder_contributions = CapitalContribution.objects.filter(
        stakeholder=stakeholder
    )
    full_name = f"{stakeholder.first_name} {stakeholder.middle_name or ''} {stakeholder.last_name}".strip()
    print(f"Capital contributions for {full_name}:")
    for contrib in stakeholder_contributions:
        print(f"  {contrib.id}: {contrib.amount} - {contrib.status} - {contrib.created_at}")