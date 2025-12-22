#!/usr/bin/env python3

import os
import sys
import django

# Add the project directory to the Python path
sys.path.append('/var/www/tradifyerp')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from accounting.models import LedgerEntry, Account, Entity, CashReceiptLine, CashPaymentLine

print("=== CHECKING CURRENT STATE AFTER CLEANUP ===")

entity = Entity.objects.filter(name__icontains='Testing').first()
print(f"Entity: {entity}")

print(f"\n=== REMAINING LEDGER ENTRIES ===")
remaining_entries = LedgerEntry.objects.filter(entity=entity).order_by('created_at')

for entry in remaining_entries:
    print(f"Entry {entry.id}: {entry.account.account_number} - {entry.entry_type} {entry.amount}")
    print(f"  Description: {entry.description}")
    print(f"  Reference: {entry.reference_number}")
    print()

print(f"\n=== WHAT SHOULD EXIST ===")
print("For Cash Receipt CR001 (100,000):")
print("  1. Capital account CREDIT 100,000 ✅")
print("  2. Cash account DEBIT 100,000 ❌ Missing!")

print("\nFor Cash Payment CP001 (200,000):")  
print("  1. Capital account DEBIT 200,000 ❌ Should be CREDIT!")
print("  2. Cash account CREDIT 200,000 ❌ Should be DEBIT!")

print(f"\n=== RECREATING MISSING CASH ENTRIES ===")

# Get the cash receipt and payment
cash_receipt = CashReceiptLine.objects.filter(reference_number='CR001').first()
cash_payment = CashPaymentLine.objects.filter(reference_number='CP001').first()
cash_account = Account.objects.filter(account_number='100001').first()

if cash_receipt and cash_account:
    # Create missing debit entry for cash receipt
    print(f"Creating cash debit entry for CR001...")
    LedgerEntry.objects.create(
        account=cash_account,
        entity=entity,
        entry_date=cash_receipt.date,
        entry_type='DEBIT',
        amount=cash_receipt.debit_amount,
        description=f'Cash Receipt: {cash_receipt.description}',
        reference_number=f'CASH-RECEIPT-{cash_receipt.id}',
        is_posted=True
    )
    print("✅ Created cash debit entry for CR001")

# Check if we need to fix the cash payment entry
if cash_payment:
    # The cash payment should CREDIT cash (reduce cash), not debit
    # Let's check what exists
    cp_entry = LedgerEntry.objects.filter(
        reference_number=f'CASH-PAYMENT-{cash_payment.id}',
        account=cash_account
    ).first()
    
    if cp_entry:
        print(f"Found cash payment entry: {cp_entry.entry_type} {cp_entry.amount}")
        if cp_entry.entry_type == 'DEBIT':
            print("❌ Cash payment incorrectly debits cash - should credit cash")
            print("Converting to credit...")
            cp_entry.entry_type = 'CREDIT'
            cp_entry.save()
            print("✅ Fixed cash payment to credit cash")

print(f"\n=== FINAL VERIFICATION ===")
from django.db.models import Sum

# Check final balances
cash_account = Account.objects.filter(account_number='100001').first()
if cash_account:
    debits = LedgerEntry.objects.filter(
        account=cash_account, entry_type='DEBIT'
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    credits = LedgerEntry.objects.filter(
        account=cash_account, entry_type='CREDIT'
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    balance = float(debits) - float(credits)
    print(f"Cash account final balance: {balance:,.2f}")
    
    expected_balance = 100000 - 200000  # Receipt +100k, Payment -200k = -100k
    print(f"Expected balance: {expected_balance:,.2f}")
    
    if abs(balance - expected_balance) < 0.01:
        print("✅ Cash balance is now CORRECT!")
    else:
        print(f"❌ Cash balance still wrong")

print(f"\n=== ALL FINAL ENTRIES ===")
final_entries = LedgerEntry.objects.filter(entity=entity).order_by('account__account_number', 'created_at')

for entry in final_entries:
    print(f"Entry {entry.id}: {entry.account.account_number} - {entry.entry_type} {entry.amount} (Ref: {entry.reference_number})")