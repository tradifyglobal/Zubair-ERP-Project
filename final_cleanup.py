#!/usr/bin/env python3

import os
import sys
import django

# Add the project directory to the Python path
sys.path.append('/var/www/tradifyerp')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from accounting.models import LedgerEntry, Account, Entity

print("=== FINAL CLEANUP - REMOVE ALL CAPITAL CONTRIBUTION LEDGER ENTRIES ===")

entity = Entity.objects.filter(name__icontains='Testing').first()

# Remove ALL capital contribution generated entries
cap_entries = LedgerEntry.objects.filter(
    entity=entity,
    reference_number__startswith='CAP-'
)

print(f"Found {cap_entries.count()} capital contribution entries to remove:")
for entry in cap_entries:
    print(f"  Entry {entry.id}: {entry.account.account_number} - {entry.entry_type} {entry.amount}")

if cap_entries.exists():
    deleted_count = cap_entries.delete()[0]
    print(f"✅ Deleted {deleted_count} capital contribution ledger entries")

print(f"\n=== FIXING CASH PAYMENT LOGIC ===")
# Fix the cash payment entry - it should CREDIT cash, not DEBIT
cash_payment_entry = LedgerEntry.objects.filter(
    entity=entity,
    reference_number='CASH-PAYMENT-12',
    account__account_number='100001'
).first()

if cash_payment_entry:
    print(f"Current cash payment entry: {cash_payment_entry.entry_type} {cash_payment_entry.amount}")
    if cash_payment_entry.entry_type == 'DEBIT':
        print("Converting cash payment from DEBIT to CREDIT (payment reduces cash)")
        cash_payment_entry.entry_type = 'CREDIT'
        cash_payment_entry.save()
        print("✅ Fixed cash payment entry")

print(f"\n=== FINAL LEDGER ENTRIES ===")
final_entries = LedgerEntry.objects.filter(entity=entity).order_by('account__account_number', 'entry_date')

print("Should have exactly 4 entries:")
print("1. Cash Receipt: Cash DEBIT 100,000")
print("2. Cash Receipt: Capital CREDIT 100,000") 
print("3. Cash Payment: Cash CREDIT 200,000")
print("4. Cash Payment: Capital CREDIT 200,000")

print(f"\nActual entries ({final_entries.count()}):")
for entry in final_entries:
    account_type = "Cash" if entry.account.account_number == '100001' else "Capital"
    print(f"  {account_type}: {entry.entry_type} {entry.amount:,.0f} (Ref: {entry.reference_number})")

print(f"\n=== FINAL CASH BALANCE ===")
from django.db.models import Sum

cash_account = Account.objects.filter(account_number='100001').first()
if cash_account:
    debits = LedgerEntry.objects.filter(
        account=cash_account, entry_type='DEBIT'
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    credits = LedgerEntry.objects.filter(
        account=cash_account, entry_type='CREDIT'
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    balance = float(debits) - float(credits)
    print(f"Cash Balance: {balance:,.2f}")
    
    # Expected: Receipt +100k, Payment -200k = -100k
    expected = 100000 - 200000  
    print(f"Expected: {expected:,.2f}")
    
    if abs(balance - expected) < 0.01:
        print("✅ CASH BALANCE IS NOW CORRECT!")
    else:
        print(f"❌ Still incorrect")

print(f"\n=== CAPITAL ACCOUNT BALANCE ===")  
capital_accounts = Account.objects.filter(
    entity=entity,
    account_type='EQUITY',
    name__icontains='Fayazuddin'
)

total_capital_credits = 0
for account in capital_accounts:
    credits = LedgerEntry.objects.filter(
        account=account, entry_type='CREDIT'
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    print(f"Capital Account {account.account_number}: {float(credits):,.2f}")
    total_capital_credits += float(credits)

print(f"Total Capital Credits: {total_capital_credits:,.2f}")
print(f"Should be: 300,000.00 (100k receipt + 200k payment)")

if abs(total_capital_credits - 300000) < 0.01:
    print("✅ CAPITAL BALANCE IS CORRECT!")
else:
    print(f"❌ Capital balance incorrect")

print(f"\n=== SUMMARY ===")
print(f"Cash Balance: {balance:,.2f} (should be -100,000)")
print(f"Capital Balance: {total_capital_credits:,.2f} (should be 300,000)")
print(f"This represents: 1 lakh receipt + 2 lakh payment = 3 lakh total capital")