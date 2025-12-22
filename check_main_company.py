#!/usr/bin/env python
"""
Check GL Dashboard for Main Company entity specifically
"""

import os
import sys
sys.path.append('/var/www/tradifyerp')

import django
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from accounting.models import Account, LedgerEntry, Entity
from shareholder.models import CapitalContribution, Stakeholder

print("GL DASHBOARD - MAIN COMPANY SPECIFIC CHECK")
print("=" * 70)

# Get Main Company entity specifically
main_company = Entity.objects.filter(name='Main Company').first()
if main_company:
    print(f"Main Company Entity: {main_company.name} (ID: {main_company.id}) Active: {main_company.is_active}")
else:
    print("Main Company not found!")
    exit(1)

# Check Fayazuddin in all entities
fayaz_list = Stakeholder.objects.filter(
    first_name__icontains='Fayaz'
).union(
    Stakeholder.objects.filter(
        last_name__icontains='Zubair'
    )
).union(
    Stakeholder.objects.filter(
        last_name__icontains='Mohammed'
    )
)

print("\nSTAKEHOLDERS MATCHING FAYAZ/ZUBAIR/MOHAMMED:")
for fayaz in fayaz_list:
    print(f"  - {fayaz.first_name} {fayaz.last_name} (ID: {fayaz.id})")
    
    # Check capital contributions for this person
    contributions = CapitalContribution.objects.filter(
        stakeholder=fayaz,
        entity=main_company
    )
    if contributions.exists():
        print(f"    Capital Contributions in Main Company:")
        for contrib in contributions:
            print(f"      {contrib.reference_number}: {contrib.amount:,} {contrib.currency.code} -> {contrib.amount_company_currency:,} [{contrib.status}]")

print(f"\nMAIN COMPANY ACCOUNTS WITH BALANCES:")
print("-" * 50)

accounts = main_company.accounts.all().order_by('account_type', 'account_number')
total_assets = Decimal('0.00')
total_equity = Decimal('0.00')
cash_total = Decimal('0.00')

for account in accounts:
    # Use GL Dashboard logic exactly
    debits = account.ledger_entries.filter(entry_type='DEBIT').aggregate(
        total=django.db.models.Sum('amount')
    )['total'] or Decimal('0.00')
    credits = account.ledger_entries.filter(entry_type='CREDIT').aggregate(
        total=django.db.models.Sum('amount')
    )['total'] or Decimal('0.00')
    
    # Same logic as GLDashboardView
    is_debit_based = account.account_type in ['ASSET', 'EXPENSE']
    
    if is_debit_based:
        current_balance = debits - credits
    else:
        current_balance = credits - debits
    
    # Track totals
    if account.account_type == 'ASSET':
        total_assets += current_balance
    elif account.account_type == 'EQUITY':
        total_equity += current_balance
    
    if 'cash' in account.name.lower():
        cash_total += current_balance
    
    if current_balance != 0:
        print(f"{account.account_type:8s} | {account.account_number:6s} | {account.name:30s} | {current_balance:>12,.2f}")
        
        # Show entries if this is a cash account or has large balance
        if 'cash' in account.name.lower() or abs(current_balance) > 250000:
            print(f"    Ledger entries:")
            entries = account.ledger_entries.all().order_by('-entry_date')[:5]
            for entry in entries:
                print(f"      {entry.entry_date} | {entry.entry_type:6s} | {entry.amount:>10,.2f} | {entry.description[:40]}")

print(f"\nSUMMARY FOR MAIN COMPANY:")
print(f"  Total Assets: {total_assets:,.2f}")
print(f"  Total Equity: {total_equity:,.2f}")
print(f"  Total Cash: {cash_total:,.2f}")

# Check if any accounts show 500,000
large_accounts = []
for account in accounts:
    debits = account.ledger_entries.filter(entry_type='DEBIT').aggregate(
        total=django.db.models.Sum('amount')
    )['total'] or Decimal('0.00')
    credits = account.ledger_entries.filter(entry_type='CREDIT').aggregate(
        total=django.db.models.Sum('amount')
    )['total'] or Decimal('0.00')
    
    is_debit_based = account.account_type in ['ASSET', 'EXPENSE']
    
    if is_debit_based:
        current_balance = debits - credits
    else:
        current_balance = credits - debits
    
    if abs(current_balance) == 500000:
        large_accounts.append((account, current_balance))

if large_accounts:
    print(f"\nACCOUNTS WITH EXACTLY 500,000 (5 LAKH):")
    for account, balance in large_accounts:
        print(f"  {account.name}: {balance:,.2f}")
else:
    print(f"\nNo accounts found with exactly 500,000 balance.")

print("\nCHECK COMPLETE!")