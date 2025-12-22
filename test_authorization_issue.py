#!/usr/bin/env python3
"""
Test the Cash Receipt Authorization functionality to identify the issue
"""
import os
import django
import sys

# Add the project directory to the Python path
sys.path.append('/var/www/tradifyerp')

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')

# Setup Django
django.setup()

# Import models
from accounting.models import CashReceiptLine, Account, LedgerEntry
from datetime import date

print("TESTING CASH RECEIPT AUTHORIZATION ISSUE")
print("=========================================")

# Get the test receipt we created earlier
try:
    test_receipt = CashReceiptLine.objects.get(id=21)
    print(f"✅ Found test receipt: ID {test_receipt.id}")
    print(f"   Status: {test_receipt.status}")
    print(f"   Workflow Status: {test_receipt.workflow_status}")
    print(f"   Debit Account: {test_receipt.account}")
    print(f"   Credit Account: {test_receipt.credit_account}")
    print(f"   Debit Amount: {test_receipt.debit_amount}")
    print(f"   Credit Amount: {test_receipt.credit_amount}")
except CashReceiptLine.DoesNotExist:
    print("❌ Test receipt not found")
    exit(1)

# Check current workflow status eligibility
print(f"\n1. CHECKING AUTHORIZATION ELIGIBILITY...")
if test_receipt.workflow_status == 'AUTHORIZED':
    print("✅ Receipt is already AUTHORIZED")
elif test_receipt.workflow_status == 'APPROVED':
    print("✅ Receipt is APPROVED - ready for authorization")
elif test_receipt.workflow_status == 'DRAFT':
    print("⚠️ Receipt is in DRAFT status - needs approval first")
    
    # Update to APPROVED for testing
    print("   Updating to APPROVED for testing...")
    test_receipt.workflow_status = 'APPROVED'
    test_receipt.save()
    print("   ✅ Updated to APPROVED")
else:
    print(f"❌ Receipt status is {test_receipt.workflow_status} - cannot authorize")

# Check if credit_account is properly set
print(f"\n2. CHECKING ACCOUNT SETUP...")
if not test_receipt.credit_account:
    print("❌ ERROR: Credit account is not set!")
    
    # Try to set it to cash account
    try:
        cash_account = Account.objects.get(
            entity=test_receipt.entity,
            account_number='100001'
        )
        print(f"✅ Found cash account: {cash_account}")
        test_receipt.credit_account = cash_account
        test_receipt.save()
        print("✅ Updated credit account to cash account")
    except Account.DoesNotExist:
        print("❌ Cash account (100001) not found!")
        exit(1)
else:
    print(f"✅ Credit account set: {test_receipt.credit_account}")

# Test manual authorization simulation
print(f"\n3. SIMULATING AUTHORIZATION PROCESS...")
try:
    print("Creating debit entry...")
    debit_entry = LedgerEntry.objects.create(
        entity=test_receipt.entity,
        account=test_receipt.account,
        entry_type='DEBIT',
        amount=test_receipt.debit_amount,
        description=f"TEST Cash Receipt: {test_receipt.description}",
        entry_date=test_receipt.date,
        reference_number=f'TEST-CASH-RECEIPT-{test_receipt.id}',
        is_posted=True,
        workflow_status='AUTHORIZED'
    )
    print(f"✅ Debit entry created: ID {debit_entry.id}")
    
    print("Creating credit entry...")
    credit_entry = LedgerEntry.objects.create(
        entity=test_receipt.entity,
        account=test_receipt.credit_account,
        entry_type='CREDIT',
        amount=test_receipt.credit_amount,
        description=f"TEST Cash Receipt: {test_receipt.description}",
        entry_date=test_receipt.date,
        reference_number=f'TEST-CASH-RECEIPT-{test_receipt.id}',
        is_posted=True,
        workflow_status='AUTHORIZED'
    )
    print(f"✅ Credit entry created: ID {credit_entry.id}")
    
    print("✅ Authorization simulation successful!")
    
except Exception as e:
    print(f"❌ Authorization simulation failed: {e}")

print(f"\n🔍 DIAGNOSIS COMPLETE")
print("Check the web interface to see if authorization button works now.")