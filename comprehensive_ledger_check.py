#!/usr/bin/env python3

import os
import sys
import django

# Add the project directory to the Python path
sys.path.append('/var/www/tradifyerp')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from accounting.models import LedgerEntry, Account
from django.db.models import Sum

print("=== COMPREHENSIVE LEDGER ANALYSIS ===")

# Find Testing entity
from accounting.models import Entity
entity = Entity.objects.filter(name__icontains='Testing').first()
entity_id = entity.id

print(f"Entity: {entity}")

print("\n=== ALL LEDGER ENTRIES FOR ENTITY ===")
all_entries = LedgerEntry.objects.filter(entity_id=entity_id).order_by('created_at')

print(f"Total ledger entries: {all_entries.count()}")

for entry in all_entries:
    print(f"Entry {entry.id}:")
    print(f"  Account: {entry.account.account_number} - {entry.account.name}")
    print(f"  Type: {entry.entry_type}")
    print(f"  Amount: {entry.amount:,.2f}")
    print(f"  Description: {entry.description}")
    print(f"  Reference: {entry.reference_number}")
    print(f"  Date: {entry.entry_date}")
    print()

print("\n=== CHECKING ACCOUNT BALANCE CALCULATION ===")

# Get all accounts in entity
accounts = Account.objects.filter(entity_id=entity_id)

for account in accounts:
    # Direct aggregation like the views do
    debits = LedgerEntry.objects.filter(
        account=account, entry_type='DEBIT'
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    credits = LedgerEntry.objects.filter(
        account=account, entry_type='CREDIT'  
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    balance = float(debits) - float(credits)
    
    if balance != 0:  # Only show accounts with activity
        print(f"Account {account.account_number} - {account.name}:")
        print(f"  Debits: {float(debits):,.2f}")
        print(f"  Credits: {float(credits):,.2f}") 
        print(f"  Balance: {balance:,.2f}")
        print()

print("\n=== CHECKING DIFFERENT FIELD NAMES ===")
# Maybe the issue is debit_amount vs amount fields?
from accounting.models import CashReceiptLine, CashPaymentLine

cash_receipts = CashReceiptLine.objects.filter(entity_id=entity_id)
cash_payments = CashPaymentLine.objects.filter(entity_id=entity_id)

print("Cash Receipts:")
for receipt in cash_receipts:
    print(f"  {receipt.reference_number}: debit_amount={receipt.debit_amount}, credit_amount={receipt.credit_amount}")
    
print("\nCash Payments:")  
for payment in cash_payments:
    print(f"  {payment.reference_number}: debit_amount={payment.debit_amount}, credit_amount={payment.credit_amount}")

# Check if views are using wrong amount field
print(f"\n=== CASH RECEIPT AGGREGATION TEST ===")
receipt_debit_sum = CashReceiptLine.objects.filter(entity_id=entity_id).aggregate(
    total=Sum('debit_amount')
)['total'] or 0
receipt_credit_sum = CashReceiptLine.objects.filter(entity_id=entity_id).aggregate(
    total=Sum('credit_amount')  
)['total'] or 0

print(f"Receipt debit_amount sum: {float(receipt_debit_sum):,.2f}")
print(f"Receipt credit_amount sum: {float(receipt_credit_sum):,.2f}")

print(f"\n=== CASH PAYMENT AGGREGATION TEST ===")
payment_debit_sum = CashPaymentLine.objects.filter(entity_id=entity_id).aggregate(
    total=Sum('debit_amount')
)['total'] or 0
payment_credit_sum = CashPaymentLine.objects.filter(entity_id=entity_id).aggregate(
    total=Sum('credit_amount')
)['total'] or 0

print(f"Payment debit_amount sum: {float(payment_debit_sum):,.2f}")
print(f"Payment credit_amount sum: {float(payment_credit_sum):,.2f}")

print(f"\n=== POTENTIAL PROBLEM ===")
total_receipts_debits = float(receipt_debit_sum)
total_payments_debits = float(payment_debit_sum)  
total_from_transactions = total_receipts_debits + total_payments_debits

print(f"If views sum debit_amount from both cash receipts and payments:")
print(f"  Cash receipts debit_amount: {total_receipts_debits:,.2f}")
print(f"  Cash payments debit_amount: {total_payments_debits:,.2f}") 
print(f"  Total: {total_from_transactions:,.2f}")
print(f"  + Capital contributions: 300,000.00")
print(f"  = Wrong total: {total_from_transactions + 300000:,.2f}")

if total_from_transactions == 300000:
    print("❌ FOUND THE ISSUE: Views are summing debit_amounts from cash transactions!")
    print("    This double counts with capital contributions.")