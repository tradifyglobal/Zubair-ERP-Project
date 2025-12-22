#!/usr/bin/env python3

import os
import sys
import django

# Add the project directory to the Python path
sys.path.append('/var/www/tradifyerp')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from accounting.models import CashPaymentLine, CapitalContribution, LedgerEntry, Account, Stakeholder, Entity, Currency
from django.utils import timezone

print("=== CREATING MISSING CAPITAL CONTRIBUTION FOR CP001 ===")

# Get the cash payment
cp001 = CashPaymentLine.objects.filter(reference_number='CP001').first()
print(f"Cash Payment CP001: {cp001.debit_amount} INR")
print(f"Account: {cp001.account}")
print(f"Credit Account: {cp001.credit_account}")

# Find the stakeholder
stakeholder = Stakeholder.objects.filter(
    entity=cp001.entity,
    first_name__icontains='Fayazuddin'
).first()

print(f"Found stakeholder: {stakeholder.first_name} {stakeholder.middle_name} {stakeholder.last_name}")

# Get currency
currency = Currency.objects.filter(code='INR').first()
print(f"Currency: {currency}")

# Check if capital contribution already exists for this amount
existing_contrib = CapitalContribution.objects.filter(
    stakeholder=stakeholder,
    entity=cp001.entity,
    amount=cp001.debit_amount
).first()

if existing_contrib:
    print(f"Existing contribution found: {existing_contrib.id} - {existing_contrib.amount}")
    
    # Update to link with cash payment
    existing_contrib.reference_number = cp001.reference_number
    existing_contrib.contribution_date = cp001.date
    existing_contrib.payment_mode = 'CASH'
    existing_contrib.status = 'COMPLETED'
    existing_contrib.workflow_status = 'APPROVED'
    existing_contrib.save()
    
    print(f"✅ Updated existing capital contribution {existing_contrib.id}")
else:
    # Create new capital contribution
    new_contrib = CapitalContribution.objects.create(
        entity=cp001.entity,
        stakeholder=stakeholder,
        contribution_date=cp001.date,
        status='COMPLETED',
        workflow_status='APPROVED',
        amount=cp001.debit_amount,
        currency=currency,
        currency_destination=currency,
        exchange_rate=1.0,
        payment_mode='CASH',
        reference_number=cp001.reference_number,
        notes=f"Auto-created from cash payment {cp001.reference_number}",
        amount_company_currency=cp001.debit_amount
    )
    
    print(f"✅ Created new capital contribution {new_contrib.id}")

print("\n=== VERIFICATION ===")
# Verify capital contributions now show the entry
contributions = CapitalContribution.objects.filter(
    entity=cp001.entity,
    stakeholder=stakeholder
).order_by('-created_at')

for contrib in contributions:
    print(f"Contribution {contrib.id}: {contrib.amount} {contrib.currency.code} - {contrib.status} - {contrib.reference_number}")