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

print("=== RESTORING MISSING CASH PAYMENT ENTRY ===")

entity = Entity.objects.filter(name__icontains='Testing').first()
cash_account = Account.objects.filter(account_number='100001').first()

print("Current cash entries:")
cash_entries = LedgerEntry.objects.filter(account=cash_account)
for entry in cash_entries:
    print(f"  Entry {entry.id}: {entry.entry_type} {entry.amount} (Ref: {entry.reference_number})")

# Check if cash payment entry exists
cp_cash_entry = LedgerEntry.objects.filter(
    account=cash_account,
    reference_number='CASH-PAYMENT-12'
).first()

print(f"\nCash payment entry exists: {cp_cash_entry is not None}")

if not cp_cash_entry:
    print("Creating missing cash debit entry for cash payment CP001...")
    LedgerEntry.objects.create(
        account=cash_account,
        entity=entity,
        entry_date='2025-12-17',
        entry_type='DEBIT',
        amount=200000,
        description='Cash Payment: Testing Cash Payment - Capital Contribution',
        reference_number='CASH-PAYMENT-12', 
        is_posted=True
    )
    print("✅ Created cash debit entry for CP001")

print(f"\n=== FINAL VERIFICATION ===")
from django.db.models import Sum

# Recheck cash balance
cash_entries = LedgerEntry.objects.filter(account=cash_account)
total_debits = 0
total_credits = 0

print("All cash entries:")
for entry in cash_entries:
    print(f"  {entry.entry_type} {entry.amount:,.0f} (Ref: {entry.reference_number})")
    if entry.entry_type == 'DEBIT':
        total_debits += float(entry.amount)
    else:
        total_credits += float(entry.amount)

cash_balance = total_debits - total_credits
print(f"\nCash Balance: {cash_balance:,.0f}")

# Check capital balance  
capital_account = Account.objects.filter(account_number='3000-11').first()
capital_credits = LedgerEntry.objects.filter(
    account=capital_account, entry_type='CREDIT'
).aggregate(total=Sum('amount'))['total'] or 0

print(f"Capital Balance: {float(capital_credits):,.0f}")

if cash_balance == 300000 and float(capital_credits) == 300000:
    print(f"\n🎉 PERFECT!")
    print(f"✅ Cash: 3,00,000 rupees")
    print(f"✅ Capital: 3,00,000 rupees") 
    print(f"✅ Represents: 1 lakh receipt + 2 lakh payment")
    print(f"✅ No more 5 lakh error!")
    print(f"")
    print(f"🏆 PROBLEM COMPLETELY RESOLVED!")
else:
    print(f"❌ Still not matching")
    print(f"Expected: Cash=300,000, Capital=300,000")
    print(f"Actual: Cash={cash_balance:,.0f}, Capital={float(capital_credits):,.0f}")