#!/usr/bin/env python
"""
Debug cash position calculation to find why it shows 200 instead of 100
"""
import os
import django
import sys
from decimal import Decimal
from django.conf import settings

# Ensure we're in the correct Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from accounting.models import LedgerEntry, Account, Entity
from django.db.models import Sum

# Get Testing entity
entity = Entity.objects.get(name="Testing")
print(f"\n{'='*60}")
print(f"DEBUGGING CASH POSITION CALCULATION")
print(f"Entity: {entity.name}")
print(f"{'='*60}")

# Get all cash accounts for this entity
cash_accounts = Account.objects.filter(
    entity_id=entity.id,
    account_type='ASSET'
).filter(
    name__icontains='cash'
) | Account.objects.filter(
    entity_id=entity.id,
    account_type='ASSET',
    account_number__startswith='100'
)

print(f"\nCash Accounts Found: {cash_accounts.count()}")
total_cash_balance = 0

for account in cash_accounts:
    print(f"\n{'-'*60}")
    print(f"Account: {account.account_number} - {account.name}")
    
    # Get ALL ledger entries for this account
    all_entries = LedgerEntry.objects.filter(account=account).order_by('-entry_date', '-id')
    print(f"Total Ledger Entries: {all_entries.count()}")
    
    # Separate by type
    debits = LedgerEntry.objects.filter(
        account=account, entry_type='DEBIT'
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    credits = LedgerEntry.objects.filter(
        account=account, entry_type='CREDIT'
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    print(f"  Debits: {debits}")
    print(f"  Credits: {credits}")
    
    balance = float(debits) - float(credits)
    print(f"  Balance (Debits - Credits): {balance}")
    
    total_cash_balance += balance
    
    # Show recent entries
    print(f"  Recent Entries:")
    for entry in all_entries[:5]:
        print(f"    {entry.entry_date} | {entry.entry_type} | {entry.amount} | {entry.reference_number}")

print(f"\n{'='*60}")
print(f"TOTAL CASH BALANCE: {total_cash_balance}")
print(f"EXPECTED: 100 (from one 100 INR cash receipt debit to customer, credit to cash)")
print(f"ACTUAL: {total_cash_balance}")

if total_cash_balance == 200:
    print(f"\n⚠️  ISSUE: The balance is DOUBLE the expected amount!")
    print(f"This suggests:")
    print(f"  1. The GL entry is being counted from BOTH debit and credit sides")
    print(f"  2. OR there are two GL entries both on the debit side")
    print(f"  3. OR the calculation is summing from wrong accounts")

print(f"\n{'='*60}")
