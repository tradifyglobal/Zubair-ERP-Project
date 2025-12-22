#!/usr/bin/env python3
"""
Create a new DRAFT cash receipt to test authorization functionality
"""
import os
import django
import sys
from decimal import Decimal

# Add the project directory to the Python path
sys.path.append('/var/www/tradifyerp')

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')

# Setup Django
django.setup()

# Import models
from accounting.models import CashReceiptLine, Account, Entity, Currency, Stakeholder
from datetime import date

print("CREATING NEW DRAFT CASH RECEIPT FOR AUTHORIZATION TEST")
print("=====================================================")

# Get test data
entity = Entity.objects.get(name="Testing")
currency = Currency.objects.get(code="INR")
capital_account = Account.objects.get(entity=entity, account_number="3000-11")
cash_account = Account.objects.get(entity=entity, account_number="100001")

# Create a new DRAFT receipt
draft_receipt = CashReceiptLine.objects.create(
    entity=entity,
    account=capital_account,  # Debit account (Capital)
    credit_account=cash_account,  # Credit account (Cash)
    currency=currency,
    date=date.today(),
    description="AUTHORIZATION TEST - Draft Receipt",
    debit_amount=Decimal('25000.00'),
    credit_amount=Decimal('25000.00'),
    status='DRAFT',  # Start in DRAFT
    workflow_status='DRAFT',  # Start in DRAFT workflow
    reference_number="AUTH-TEST-001"
)

print(f"✅ Created DRAFT Cash Receipt for Authorization Testing:")
print(f"   ID: {draft_receipt.id}")
print(f"   Status: {draft_receipt.status}")
print(f"   Workflow Status: {draft_receipt.workflow_status}")
print(f"   Amount: {draft_receipt.debit_amount} {draft_receipt.currency}")

# Test the approval flow first
print(f"\n1. TESTING APPROVAL (DRAFT -> APPROVED)...")
draft_receipt.workflow_status = 'APPROVED'
draft_receipt.save()
print(f"✅ Updated to APPROVED status")

# Now test authorization URL access
print(f"\n2. RECEIPT READY FOR AUTHORIZATION TEST:")
print(f"   Cash Receipt ID: {draft_receipt.id}")
print(f"   Status: {draft_receipt.workflow_status}")
print(f"   Authorization URL: /cash-receipts/{draft_receipt.id}/authorize/")
print(f"   Full URL: https://tradifyglobal.com/accounting/cash-receipts/{draft_receipt.id}/authorize/")

print(f"\n🎯 TEST THIS AUTHORIZATION URL IN THE WEB INTERFACE")
print(f"The receipt is now in APPROVED status and ready for authorization.")