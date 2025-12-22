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

print("=== FINAL CASH RECEIPT FIX ===")

entity = Entity.objects.filter(name__icontains='Testing').first()
cash_account = Account.objects.filter(account_number='100001').first()

# The cash receipt CR001 needs a corresponding cash account entry
# Currently it only has: Dr. Capital, Cr. Capital (internal transfer)
# It should be: Dr. Cash, Cr. Capital (capital contribution received)

# Check if cash receipt already has a cash entry
cr_cash_entry = LedgerEntry.objects.filter(
    reference_number='CASH-RECEIPT-20',
    account=cash_account
).first()

print(f"Cash receipt cash entry exists: {cr_cash_entry is not None}")

if not cr_cash_entry:
    print("Creating missing cash debit entry for cash receipt CR001...")
    LedgerEntry.objects.create(
        account=cash_account,
        entity=entity,
        entry_date='2025-12-17',
        entry_type='DEBIT',
        amount=100000,
        description='Cash Receipt: Test 1 - Capital Contribution',
        reference_number='CASH-RECEIPT-20',
        is_posted=True
    )
    print("✅ Created cash debit entry")

# Fix the cash receipt capital entry - remove the duplicate
cr_capital_entries = LedgerEntry.objects.filter(
    reference_number='CASH-RECEIPT-20',
    account__account_number='3000-11'
)

print(f"Capital entries for CR001: {cr_capital_entries.count()}")

if cr_capital_entries.count() > 1:
    print("Removing duplicate capital entry...")
    # Keep only one
    cr_capital_entries.exclude(id=cr_capital_entries.first().id).delete()
    print("✅ Removed duplicate")

print(f"\n=== FINAL STATE CHECK ===")
from django.db.models import Sum

# Check cash balance
debits = LedgerEntry.objects.filter(
    account=cash_account, entry_type='DEBIT'
).aggregate(total=Sum('amount'))['total'] or 0

credits = LedgerEntry.objects.filter(
    account=cash_account, entry_type='CREDIT'
).aggregate(total=Sum('amount'))['total'] or 0

cash_balance = float(debits) - float(credits)
print(f"Cash Balance: {cash_balance:,.2f}")

# Check capital balance
capital_accounts = Account.objects.filter(
    entity=entity,
    account_number='3000-11'
)

total_capital = 0
for account in capital_accounts:
    credits = LedgerEntry.objects.filter(
        account=account, entry_type='CREDIT'
    ).aggregate(total=Sum('amount'))['total'] or 0
    total_capital += float(credits)

print(f"Capital Balance: {total_capital:,.2f}")

print(f"\n=== EXPECTED vs ACTUAL ===")
print("Expected:")
print("  Cash Balance: 300,000 (100k + 200k contributions)")
print("  Capital Balance: 300,000 (100k + 200k contributions)")

print(f"\nActual:")
print(f"  Cash Balance: {cash_balance:,.0f}")
print(f"  Capital Balance: {total_capital:,.0f}")

if abs(cash_balance - 300000) < 1 and abs(total_capital - 300000) < 1:
    print(f"\n🎉 SUCCESS!")
    print(f"✅ Cash shows 3,00,000 (correct)")
    print(f"✅ Capital shows 3,00,000 (correct)")
    print(f"✅ No more 5,00,000 error!")
else:
    print(f"\n❌ Still needs adjustment")

print(f"\n=== ALL FINAL ENTRIES ===")
final_entries = LedgerEntry.objects.filter(entity=entity).order_by('account__account_number', 'created_at')
for entry in final_entries:
    acc_type = "CASH" if entry.account.account_number == '100001' else "CAPITAL"
    print(f"  {acc_type}: {entry.entry_type} {entry.amount:,.0f} (Ref: {entry.reference_number})")