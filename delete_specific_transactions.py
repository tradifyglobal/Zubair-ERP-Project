#!/usr/bin/env python3
"""
Delete specific cash payment and cash receipt entries for Fayazuddin Zubair Mohammed
Dec 17, 2025 transactions
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
from accounting.models import CashReceiptLine, CashPaymentLine, LedgerEntry
from datetime import date

print("DELETING SPECIFIC TRANSACTIONS")
print("========================================")

# Target date
target_date = date(2025, 12, 17)

# Find and delete Cash Receipt: "Test 1" - 100,000 INR
print("\n1. SEARCHING FOR CASH RECEIPT...")
cash_receipts = CashReceiptLine.objects.filter(
    date=target_date,
    description__icontains="Test 1",
    debit_amount=Decimal('100000.00')
)

print(f"Found {cash_receipts.count()} matching cash receipts:")
for receipt in cash_receipts:
    print(f"  - ID: {receipt.id}")
    print(f"  - Date: {receipt.date}")
    print(f"  - Description: {receipt.description}")
    print(f"  - Debit Amount: {receipt.debit_amount} {receipt.currency}")
    print(f"  - Account: {receipt.account}")
    print(f"  - Status: {receipt.status}")
    
    # Check for related ledger entries by description/date match
    ledger_entries = LedgerEntry.objects.filter(
        entity=receipt.entity,
        entry_date=receipt.date,
        description__icontains=receipt.description
    )
    print(f"  - Related ledger entries: {ledger_entries.count()}")
    
    # Delete related ledger entries first
    if ledger_entries.exists():
        print(f"  - Deleting {ledger_entries.count()} related ledger entries...")
        ledger_entries.delete()
    
    # Delete the cash receipt
    print(f"  - Deleting cash receipt ID {receipt.id}...")
    receipt.delete()
    print(f"  ✅ Cash receipt deleted")

# Find and delete Cash Payment: "Testing Cash Payment" - 200,000 INR
print("\n2. SEARCHING FOR CASH PAYMENT...")
cash_payments = CashPaymentLine.objects.filter(
    date=target_date,
    description__icontains="Testing Cash Payment",
    debit_amount=Decimal('200000.00')
)

print(f"Found {cash_payments.count()} matching cash payments:")
for payment in cash_payments:
    print(f"  - ID: {payment.id}")
    print(f"  - Date: {payment.date}")
    print(f"  - Description: {payment.description}")
    print(f"  - Debit Amount: {payment.debit_amount} {payment.currency}")
    print(f"  - Status: {payment.status}")
    
    # Check for related ledger entries by description/date match
    ledger_entries = LedgerEntry.objects.filter(
        entity=payment.entity,
        entry_date=payment.date,
        description__icontains=payment.description
    )
    print(f"  - Related ledger entries: {ledger_entries.count()}")
    
    # Delete related ledger entries first
    if ledger_entries.exists():
        print(f"  - Deleting {ledger_entries.count()} related ledger entries...")
        ledger_entries.delete()
    
    # Delete the cash payment
    print(f"  - Deleting cash payment ID {payment.id}...")
    payment.delete()
    print(f"  ✅ Cash payment deleted")

# Verify deletion
print("\n3. VERIFICATION...")
remaining_receipts = CashReceiptLine.objects.filter(
    date=target_date,
    description__icontains="Test 1"
)
remaining_payments = CashPaymentLine.objects.filter(
    date=target_date,
    description__icontains="Testing Cash Payment"
)

print(f"Remaining cash receipts with 'Test 1': {remaining_receipts.count()}")
print(f"Remaining cash payments with 'Testing Cash Payment': {remaining_payments.count()}")

if remaining_receipts.count() == 0 and remaining_payments.count() == 0:
    print("\n✅ SUCCESS: Both transactions have been deleted!")
else:
    print("\n❌ WARNING: Some transactions may still exist")

print("\nDeletion complete.")