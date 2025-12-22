#!/usr/bin/env python
"""
Check GL Dashboard calculations for Fayazuddin Zubair Mohammed
"""

import os
import django
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from accounting.models import Account, LedgerEntry, Entity
from shareholder.models import CapitalContribution, Stakeholder

print("GL DASHBOARD CALCULATION CHECK")
print("=" * 70)

# Get the entity (find any active entity)
entities = Entity.objects.filter(is_active=True)
print("Available entities:")
for e in entities:
    print(f"  - {e.name} (ID: {e.id})")

entity = entities.first()
if not entity:
    print("No active entities found!")
    exit(1)
print(f"Using Entity: {entity.name} (ID: {entity.id})")

# Find Fayazuddin
fayaz = Stakeholder.objects.filter(
    first_name__icontains='Fayazuddin', 
    last_name__icontains='Zubair'
).first()
print(f"Stakeholder: {fayaz.first_name} {fayaz.last_name} (ID: {fayaz.id})")
print()

# Check his capital contributions
print("CAPITAL CONTRIBUTIONS:")
print("-" * 50)
contributions = CapitalContribution.objects.filter(stakeholder=fayaz)
for contrib in contributions:
    print(f"{contrib.reference_number}: {contrib.amount:,} {contrib.currency.code} "
          f"→ {contrib.amount_company_currency:,} {entity.company_currency.code} "
          f"[{contrib.status}]")

total_capital = sum(c.amount_company_currency for c in contributions if c.status == 'COMPLETED')
print(f"TOTAL CAPITAL CONTRIBUTIONS: {total_capital:,} {entity.company_currency.code}")
print()

# Check ALL accounts - especially cash and equity
print("ALL ACCOUNT BALANCES (GL Dashboard Logic):")
print("-" * 60)

accounts = entity.accounts.all().order_by('account_type', 'account_number')
total_by_type = {}

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
    
    if current_balance != 0:  # Only show accounts with balances
        print(f"{account.account_type:8s} | {account.account_number:6s} | {account.name:30s} | {current_balance:>12,.2f}")

print()
print("TOTALS BY ACCOUNT TYPE:")
print("-" * 40)
for acc_type, total in total_by_type.items():
    print(f"{acc_type:12s}: {total:>12,.2f}")

print()

# Check specific ledger entries related to Fayazuddin
print("LEDGER ENTRIES RELATED TO FAYAZUDDIN:")
print("-" * 50)

fayaz_entries = LedgerEntry.objects.filter(
    django.db.models.Q(description__icontains='fayazuddin') |
    django.db.models.Q(description__icontains='zubair') |
    django.db.models.Q(capital_contribution__stakeholder=fayaz)
).order_by('entry_date', 'id')

for entry in fayaz_entries:
    print(f"ID: {entry.id:3d} | {entry.entry_date} | {entry.account.name:25s} | "
          f"{entry.entry_type:6s} | {entry.amount:>10,.2f} | {entry.description[:40]}")

print()
print("LOOKING FOR CALCULATION ISSUES:")
print("-" * 40)

# Check if any accounts are showing 5 lakh (500,000)
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
    
    if abs(current_balance - 500000) < 1000:  # Close to 5 lakh
        print(f"WARNING POTENTIAL 5 LAKH ERROR: {account.name} = {current_balance:,.2f}")
        print(f"   Debits: {debits:,.2f}, Credits: {credits:,.2f}")
        
        # Show related entries
        entries = account.ledger_entries.all()
        for entry in entries:
            print(f"   -> {entry.entry_date} | {entry.entry_type:6s} | {entry.amount:>10,.2f} | {entry.description[:30]}")

print("\nVERIFICATION COMPLETE!")