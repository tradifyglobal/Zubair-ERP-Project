#!/usr/bin/env python3
"""
Verify deletion of specific transactions and check current state
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
from accounting.models import CashReceiptLine, CashPaymentLine, LedgerEntry, Account
from datetime import date

print("VERIFICATION OF TRANSACTION DELETION")
print("=========================================")

# Check for any remaining transactions on Dec 17, 2025
target_date = date(2025, 12, 17)

print(f"\n1. CHECKING REMAINING TRANSACTIONS FOR {target_date}...")

# Check cash receipts
all_receipts = CashReceiptLine.objects.filter(date=target_date)
print(f"Total cash receipts on {target_date}: {all_receipts.count()}")
if all_receipts.exists():
    for receipt in all_receipts:
        print(f"  - {receipt.description}: {receipt.debit_amount} {receipt.currency}")

# Check cash payments
all_payments = CashPaymentLine.objects.filter(date=target_date)
print(f"Total cash payments on {target_date}: {all_payments.count()}")
if all_payments.exists():
    for payment in all_payments:
        print(f"  - {payment.description}: {payment.debit_amount} {payment.currency}")

# Check Fayazuddin's account balance
print(f"\n2. CHECKING FAYAZUDDIN'S ACCOUNT...")
try:
    fayaz_account = Account.objects.get(account_number='3000-11')
    print(f"Account: {fayaz_account.account_number} - {fayaz_account.name}")
    
    # Check recent transactions
    recent_ledger = LedgerEntry.objects.filter(
        account=fayaz_account,
        entry_date__gte=target_date
    ).order_by('-entry_date', '-created_at')
    
    print(f"Recent ledger entries (from {target_date}): {recent_ledger.count()}")
    for entry in recent_ledger[:5]:  # Show last 5 entries
        print(f"  - {entry.entry_date}: {entry.entry_type} {entry.amount} - {entry.description}")
        
except Account.DoesNotExist:
    print("Fayazuddin's account (3000-11) not found")

print("\nVerification complete.")