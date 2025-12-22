#!/usr/bin/env python3

import os
import sys
import django

# Add the project directory to the Python path
sys.path.append('/var/www/tradifyerp')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from accounting.models import CashPaymentLine, Entity, LedgerEntry, Account
from django.db.models import Q

print("=== CHECKING CASH PAYMENT CP001 ===")

# Check the actual cash payment entry
cash_payment = CashPaymentLine.objects.filter(reference_number='CP001').first()
if cash_payment:
    print(f"Cash Payment Found:")
    print(f"  ID: {cash_payment.id}")
    print(f"  Reference: {cash_payment.reference_number}")
    print(f"  Date: {cash_payment.date}")
    print(f"  Description: {cash_payment.description}")
    print(f"  Debit Amount: {cash_payment.debit_amount}")
    print(f"  Credit Amount: {cash_payment.credit_amount}")
    print(f"  Credit Account: {cash_payment.credit_account}")
    print(f"  Amount: {cash_payment.amount} {cash_payment.currency}")
    print(f"  Status: {cash_payment.workflow_status}")
    print(f"  Entity: {cash_payment.entity}")
    print()

print("=== CHECKING CASH POSITION VIEW LOGIC ===")

# Check what accounts are being used for cash position
cash_accounts = Account.objects.filter(
    Q(account_name__icontains='cash') | 
    Q(account_name__icontains='bank') |
    Q(account_number__startswith='1001')
).order_by('account_number')

print(f"Cash-related accounts found: {cash_accounts.count()}")
for account in cash_accounts:
    print(f"  {account.account_number} - {account.account_name} (Type: {account.account_type})")
    
    # Check ledger entries for this account
    entries = LedgerEntry.objects.filter(account=account).order_by('-date')[:3]
    for entry in entries:
        print(f"    Entry: {entry.reference_number} - Debit: {entry.debit_amount} Credit: {entry.credit_amount}")

print("\n=== CHECKING LEDGER ENTRIES FOR CP001 ===")
ledger_entries = LedgerEntry.objects.filter(reference_number='CP001')
print(f"Ledger entries for CP001: {ledger_entries.count()}")
for entry in ledger_entries:
    print(f"  Account: {entry.account.account_number} - {entry.account.account_name}")
    print(f"  Debit: {entry.debit_amount}, Credit: {entry.credit_amount}")
    print(f"  Entity: {entry.entity}")
    print(f"  Date: {entry.date}")
    print()