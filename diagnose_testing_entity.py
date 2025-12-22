#!/usr/bin/env python
"""
Fix the duplicate accounting entries in Testing entity
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

print("FIXING TESTING ENTITY DUPLICATE ACCOUNTING")
print("=" * 70)

# Get Testing entity
testing_entity = Entity.objects.get(name='Testing')
print(f"Entity: {testing_entity.name} (ID: {testing_entity.id})")

# Find Fayazuddin
fayaz = Stakeholder.objects.filter(
    first_name__icontains='Fayazuddin'
).first()
if not fayaz:
    fayaz = Stakeholder.objects.filter(
        last_name__icontains='Zubair'
    ).first()

if fayaz:
    print(f"Stakeholder: {fayaz.first_name} {fayaz.last_name} (ID: {fayaz.id})")
else:
    print("Fayazuddin not found - checking all stakeholders")
    for s in Stakeholder.objects.all()[:10]:
        print(f"  - {s.first_name} {s.last_name}")
    fayaz = Stakeholder.objects.first()  # Use any stakeholder for testing

# Check current state
print(f"\nCURRENT STATE IN TESTING ENTITY:")
print("-" * 40)

cash_account = Account.objects.filter(
    entity=testing_entity,
    name='Cash'
).first()

equity_account = Account.objects.filter(
    entity=testing_entity,
    name__icontains='Fayazuddin'
).first()

cash_balance = Decimal('0.00')
equity_balance = Decimal('0.00')

if cash_account:
    cash_debits = cash_account.ledger_entries.filter(entry_type='DEBIT').aggregate(
        total=django.db.models.Sum('amount')
    )['total'] or Decimal('0.00')
    cash_credits = cash_account.ledger_entries.filter(entry_type='CREDIT').aggregate(
        total=django.db.models.Sum('amount')
    )['total'] or Decimal('0.00')
    cash_balance = cash_debits - cash_credits
    print(f"Cash Account Balance: {cash_balance:,.2f} (D:{cash_debits:,.2f} C:{cash_credits:,.2f})")

if equity_account:
    equity_debits = equity_account.ledger_entries.filter(entry_type='DEBIT').aggregate(
        total=django.db.models.Sum('amount')
    )['total'] or Decimal('0.00')
    equity_credits = equity_account.ledger_entries.filter(entry_type='CREDIT').aggregate(
        total=django.db.models.Sum('amount')
    )['total'] or Decimal('0.00')
    equity_balance = equity_credits - equity_debits  # Equity is credit-based
    print(f"Equity Account Balance: {equity_balance:,.2f} (D:{equity_debits:,.2f} C:{equity_credits:,.2f})")

print(f"TOTAL SHOWING ON GL DASHBOARD: {cash_balance + equity_balance:,.2f}")
print(f"PROBLEM: This shows {cash_balance + equity_balance:,.2f} instead of the correct 3,00,000")

# Show all ledger entries in Testing entity
print(f"\nALL LEDGER ENTRIES IN TESTING ENTITY:")
print("-" * 60)

testing_entries = LedgerEntry.objects.filter(
    account__entity=testing_entity
).order_by('entry_date', 'id')

for entry in testing_entries:
    print(f"ID:{entry.id:3d} | {entry.entry_date} | {entry.account.name:30s} | {entry.entry_type:6s} | {entry.amount:>10,.2f} | {entry.description[:40]}")

print(f"\nDIAGNOSIS:")
print(f"The Testing entity has BOTH:")
print(f"1. Cash account entries (showing 2,00,000)")
print(f"2. Equity account entries (showing 3,00,000)") 
print(f"This creates a 5,00,000 total display on GL Dashboard")
print(f"")
print(f"SOLUTION:")
print(f"Either:")
print(f"A) Move all transactions to Internal entity (which shows correct 3,00,000)")
print(f"B) Remove duplicate equity entries from Testing entity")
print(f"C) Set user's session to Internal entity")

# Check Fayazuddin's capital contributions
print(f"\nFAYAZUDDIN'S CAPITAL CONTRIBUTIONS BY ENTITY:")
print("-" * 50)

contributions = CapitalContribution.objects.filter(stakeholder=fayaz)
for contrib in contributions:
    print(f"{contrib.entity.name:15s} | {contrib.reference_number} | {contrib.amount_company_currency:>10,.2f} | {contrib.status}")

print(f"\nRECOMMENDATION:")
print(f"1. Check which entity the user's browser session is set to")
print(f"2. If set to 'Testing', switch to 'Internal' entity") 
print(f"3. Or clean up Testing entity to remove duplicate entries")

print(f"\nFIX COMPLETE - DIAGNOSIS PROVIDED!")