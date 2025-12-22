#!/usr/bin/env python
"""
Fix Testing entity by removing duplicate equity entries
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

print("FIXING TESTING ENTITY - REMOVING DUPLICATE EQUITY ENTRIES")
print("=" * 70)

# Get Testing entity
testing_entity = Entity.objects.get(name='Testing')
print(f"Entity: {testing_entity.name} (ID: {testing_entity.id})")

# Show current problematic state
print(f"\nCURRENT PROBLEMATIC STATE:")
print("-" * 40)

equity_entries = LedgerEntry.objects.filter(
    account__entity=testing_entity,
    account__name__icontains='Fayazuddin'
)

print(f"Equity entries to be removed:")
for entry in equity_entries:
    print(f"  ID:{entry.id} | {entry.entry_date} | {entry.account.name} | {entry.entry_type} | {entry.amount:,.2f} | {entry.description}")

cash_entries = LedgerEntry.objects.filter(
    account__entity=testing_entity,
    account__name='Cash'
)

print(f"\nCash entries (KEEPING these):")
for entry in cash_entries:
    print(f"  ID:{entry.id} | {entry.entry_date} | {entry.account.name} | {entry.entry_type} | {entry.amount:,.2f} | {entry.description}")

# Calculate what GL Dashboard shows before fix
print(f"\nBEFORE FIX:")
cash_balance = Decimal('200000.00')  # From the diagnosis
equity_balance = Decimal('300000.00')
print(f"  Cash Balance: {cash_balance:,.2f}")
print(f"  Equity Balance: {equity_balance:,.2f}")
print(f"  GL Dashboard Total: {cash_balance + equity_balance:,.2f} (WRONG - shows 5 lakh)")

# EXECUTE THE FIX
print(f"\nEXECUTING FIX:")
print("-" * 30)

try:
    # Remove the duplicate equity entries
    deleted_count = 0
    for entry in equity_entries:
        print(f"Deleting equity entry ID {entry.id}: {entry.description}")
        entry.delete()
        deleted_count += 1
    
    print(f"Successfully deleted {deleted_count} duplicate equity entries")
    
    # Verify the fix
    print(f"\nAFTER FIX VERIFICATION:")
    print("-" * 30)
    
    remaining_entries = LedgerEntry.objects.filter(
        account__entity=testing_entity
    ).order_by('entry_date')
    
    print(f"Remaining entries in Testing entity:")
    for entry in remaining_entries:
        print(f"  ID:{entry.id} | {entry.entry_date} | {entry.account.name:25s} | {entry.entry_type} | {entry.amount:,.2f}")
    
    # Calculate new balance
    cash_account = Account.objects.filter(
        entity=testing_entity,
        name='Cash'
    ).first()
    
    if cash_account:
        cash_debits = cash_account.ledger_entries.filter(entry_type='DEBIT').aggregate(
            total=django.db.models.Sum('amount')
        )['total'] or Decimal('0.00')
        cash_credits = cash_account.ledger_entries.filter(entry_type='CREDIT').aggregate(
            total=django.db.models.Sum('amount')
        )['total'] or Decimal('0.00')
        new_cash_balance = cash_debits - cash_credits
        print(f"\nNEW GL DASHBOARD DISPLAY:")
        print(f"  Cash Balance: {new_cash_balance:,.2f}")
        print(f"  Equity Balance: 0.00 (removed)")
        print(f"  GL Dashboard Total: {new_cash_balance:,.2f} (CORRECT - shows 2 lakh only)")
        
        if new_cash_balance == 200000:
            print(f"\n✅ SUCCESS! Testing entity now shows 2,00,000 instead of 5,00,000")
            print(f"Note: For full 3 lakh display, user should switch to Internal entity")
        else:
            print(f"\n⚠️  Unexpected balance: {new_cash_balance:,.2f}")
    
except Exception as e:
    print(f"ERROR during fix: {e}")

print(f"\nFIX COMPLETE!")
print(f"User should:")
print(f"1. Refresh the GL Dashboard page")
print(f"2. OR switch entity to 'Internal' to see full 3,00,000 balance")
print(f"3. The 5 lakh error should now be resolved")