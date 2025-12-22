#!/usr/bin/env python
"""
Check GL Dashboard calculations for Fayazuddin Zubair Mohammed - Remote Version
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

print("GL DASHBOARD CALCULATION CHECK")
print("=" * 70)

# Get available entities
entities = Entity.objects.all()
print("Available entities:")
for e in entities:
    print(f"  - {e.name} (ID: {e.id}) Active: {e.is_active}")

entity = entities.filter(is_active=True).first()
if not entity:
    print("No active entities found!")
    exit(1)
print(f"Using Entity: {entity.name} (ID: {entity.id})")
print()

# Find Fayazuddin
fayaz = Stakeholder.objects.filter(
    first_name__icontains='Fayazuddin', 
    last_name__icontains='Zubair'
).first()

if fayaz:
    print(f"Stakeholder: {fayaz.first_name} {fayaz.last_name} (ID: {fayaz.id})")
else:
    print("Fayazuddin not found!")
    # Show all stakeholders
    stakeholders = Stakeholder.objects.all()[:5]
    print("Available stakeholders:")
    for s in stakeholders:
        print(f"  - {s.first_name} {s.last_name}")
print()

# Check ALL account balances using GL Dashboard logic
print("ALL ACCOUNT BALANCES (GL Dashboard Logic):")
print("-" * 60)

accounts = entity.accounts.all().order_by('account_type', 'account_number')
total_by_type = {}
cash_accounts_found = []

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
    
    if account.account_type not in total_by_type:
        total_by_type[account.account_type] = Decimal('0.00')
    total_by_type[account.account_type] += current_balance
    
    # Track cash accounts
    if 'cash' in account.name.lower():
        cash_accounts_found.append(account)
    
    if current_balance != 0 or 'cash' in account.name.lower():  # Show all cash accounts and non-zero accounts
        print(f"{account.account_type:8s} | {account.account_number:6s} | {account.name:30s} | {current_balance:>12,.2f}")

print()
print("TOTALS BY ACCOUNT TYPE:")
print("-" * 40)
for acc_type, total in total_by_type.items():
    print(f"{acc_type:12s}: {total:>12,.2f}")

print()

# Check for potential 500,000 issue
print("LOOKING FOR CALCULATION ISSUES:")
print("-" * 40)

suspicious_balances = []
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
    
    # Check for 5 lakh (500,000) or other suspicious amounts
    if abs(current_balance) >= 400000:  # 4 lakh or more
        suspicious_balances.append((account, current_balance, debits, credits))

if suspicious_balances:
    print("SUSPICIOUS LARGE BALANCES:")
    for account, balance, debits, credits in suspicious_balances:
        print(f"Account: {account.name}")
        print(f"  Balance: {balance:,.2f} (Debits: {debits:,.2f}, Credits: {credits:,.2f})")
        
        # Show entries for this account
        entries = account.ledger_entries.all()[:10]
        print(f"  Recent entries ({entries.count()} total):")
        for entry in entries:
            print(f"    {entry.entry_date} | {entry.entry_type:6s} | {entry.amount:>10,.2f} | {entry.description[:40]}")
        print()
else:
    print("No suspicious large balances found.")

print("VERIFICATION COMPLETE!")