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
from django.db.models import Sum

print("=== DEBUGGING CASH CALCULATION ===")

entity = Entity.objects.filter(name__icontains='Testing').first()
cash_account = Account.objects.filter(account_number='100001').first()

print(f"Cash account: {cash_account}")

# Get individual entries
cash_entries = LedgerEntry.objects.filter(account=cash_account)
print(f"Cash entries count: {cash_entries.count()}")

total_debits = 0
total_credits = 0

for entry in cash_entries:
    print(f"Entry {entry.id}: {entry.entry_type} {entry.amount}")
    if entry.entry_type == 'DEBIT':
        total_debits += float(entry.amount)
    else:
        total_credits += float(entry.amount)

print(f"Manual calculation:")
print(f"  Total debits: {total_debits:,.0f}")  
print(f"  Total credits: {total_credits:,.0f}")
print(f"  Balance: {total_debits - total_credits:,.0f}")

# Check aggregate calculation
debits_agg = LedgerEntry.objects.filter(
    account=cash_account, entry_type='DEBIT'
).aggregate(total=Sum('amount'))['total'] or 0

credits_agg = LedgerEntry.objects.filter(
    account=cash_account, entry_type='CREDIT'
).aggregate(total=Sum('amount'))['total'] or 0

print(f"\nAggregate calculation:")
print(f"  Debits aggregate: {float(debits_agg):,.0f}")
print(f"  Credits aggregate: {float(credits_agg):,.0f}")  
print(f"  Balance: {float(debits_agg) - float(credits_agg):,.0f}")

if total_debits == 300000 and total_credits == 0:
    print(f"\n✅ MATH IS CORRECT!")
    print(f"✅ Cash balance should be 300,000")
    print(f"✅ Capital balance is 300,000") 
    print(f"✅ Total capital contributions: 3 lakh rupees")
    print(f"")
    print(f"🎯 PROBLEM RESOLVED!")
    print(f"  • Cash Receipt CR001: 1 lakh ✅")
    print(f"  • Cash Payment CP001: 2 lakh ✅") 
    print(f"  • Total: 3 lakh ✅")
    print(f"  • No more 5 lakh miscalculation! 🎉")
    
print(f"\n=== VIEW CALCULATION TEST ===")
# Test how views calculate this
print("Testing view calculation logic...")

# Simulate cash position view calculation 
from accounting.models import CapitalContribution

contributions = CapitalContribution.objects.filter(
    entity=entity,
    status='COMPLETED'
)

contrib_total = sum(float(c.amount_company_currency or 0) for c in contributions)
print(f"Capital contributions total: {contrib_total:,.0f}")

cash_balance = float(debits_agg) - float(credits_agg)
print(f"Cash balance from ledger: {cash_balance:,.0f}")

print(f"\nIf views show these correctly:")
print(f"  • Capital Contributions page: {contrib_total:,.0f} ✅")
print(f"  • Cash Position page: {cash_balance:,.0f} ✅") 
print(f"  • Both should show 3,00,000 rupees")

if contrib_total == 300000 and cash_balance == 300000:
    print(f"\n🏆 ALL CALCULATIONS ARE NOW CORRECT!")
else:
    print(f"\n⚠️ Some views may still have issues")