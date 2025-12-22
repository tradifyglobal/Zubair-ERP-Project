#!/usr/bin/env python3
"""
Create a final test receipt in APPROVED status for web interface testing
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
from accounting.models import CashReceiptLine, Account, Entity, Currency
from datetime import date

print("CREATING FINAL TEST RECEIPT FOR WEB AUTHORIZATION")
print("================================================")

# Get test data
entity = Entity.objects.get(name="Testing")
currency = Currency.objects.get(code="INR")
capital_account = Account.objects.get(entity=entity, account_number="3000-11")
cash_account = Account.objects.get(entity=entity, account_number="100001")

# Create a new receipt ready for authorization
ready_receipt = CashReceiptLine.objects.create(
    entity=entity,
    account=capital_account,
    credit_account=cash_account,
    currency=currency,
    date=date.today(),
    description="WEB AUTHORIZATION TEST - Ready for Authorization",
    debit_amount=Decimal('15000.00'),
    credit_amount=Decimal('15000.00'),
    status='DRAFT',
    workflow_status='APPROVED',  # Set directly to APPROVED
    reference_number="WEB-AUTH-001"
)

print(f"✅ Created test receipt ready for web authorization:")
print(f"   ID: {ready_receipt.id}")
print(f"   Status: {ready_receipt.status}")
print(f"   Workflow Status: {ready_receipt.workflow_status}")
print(f"   Amount: {ready_receipt.debit_amount} {ready_receipt.currency}")
print(f"   Description: {ready_receipt.description}")

print(f"\n🎯 WEB INTERFACE TEST RECEIPT:")
print(f"   Receipt ID: {ready_receipt.id}")
print(f"   Visit: https://tradifyglobal.com/accounting/cash-receipts/")
print(f"   Look for receipt with description: '{ready_receipt.description}'")
print(f"   Click the AUTHORIZE button (green arrow) to test authorization")

print(f"\n✅ AUTHORIZATION FIX DEPLOYED AND READY FOR TESTING!")