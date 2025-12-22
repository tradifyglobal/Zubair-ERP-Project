#!/usr/bin/env python3
"""
Debug GL Dashboard - Check why entries aren't showing
"""
import os
import django
import sys
from decimal import Decimal

# Add the project directory to the Python path
sys.path.append('/var/www/tradifyerp')

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')

# Setup Django
django.setup()

# Import models
from accounting.models import Entity, LedgerEntry, Account
from django.db.models import Sum

print("DEBUGGING GL DASHBOARD")
print("=====================")

# Get Testing entity
entity = Entity.objects.get(name="Testing")
print(f"Entity: {entity.name} (ID: {entity.id}, Active: {entity.is_active})")

# Get ledger entries
print(f"\n1. LEDGER ENTRIES FOR ENTITY:")
entries = LedgerEntry.objects.filter(entity=entity)
print(f"Total entries: {entries.count()}")

for entry in entries.order_by('-entry_date', '-id'):
    print(f"\n  ID {entry.id}:")
    print(f"    Date: {entry.entry_date}")
    print(f"    Account: {entry.account.account_number} - {entry.account.name}")
    print(f"    Type: {entry.entry_type}")
    print(f"    Amount: {entry.amount}")
    print(f"    Description: {entry.description}")

# Check account balances
print(f"\n2. ACCOUNT BALANCES (from GL entries):")
accounts = entity.accounts.all()
print(f"Total accounts in entity: {accounts.count()}")

accounts_with_entries = []
for account in accounts:
    debits = account.ledger_entries.filter(entry_type='DEBIT').aggregate(
        total=Sum('amount')
    )['total'] or Decimal('0.00')
    credits = account.ledger_entries.filter(entry_type='CREDIT').aggregate(
        total=Sum('amount')
    )['total'] or Decimal('0.00')
    
    if debits > 0 or credits > 0:
        print(f"\n  {account.account_number} - {account.name}:")
        print(f"    Debits: {debits}")
        print(f"    Credits: {credits}")
        print(f"    Type: {account.account_type}")
        accounts_with_entries.append(account)

print(f"\nAccounts with entries: {len(accounts_with_entries)}")

# Check the specific account for our entry
print(f"\n3. CHECKING SAJAZ ACCOUNT (3000-01):")
try:
    sajaz_account = Account.objects.get(entity=entity, account_number='3000-01')
    print(f"Account found: {sajaz_account.name}")
    
    # Get all entries for this account
    account_entries = sajaz_account.ledger_entries.all()
    print(f"Entries for this account: {account_entries.count()}")
    
    for entry in account_entries:
        print(f"  - ID {entry.id}: {entry.entry_type} {entry.amount} ({entry.description})")
    
    # Calculate balance
    debits = account_entries.filter(entry_type='DEBIT').aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    credits = account_entries.filter(entry_type='CREDIT').aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    balance = credits - debits  # For EQUITY accounts
    
    print(f"\nAccount balance calculation:")
    print(f"  Debits: {debits}")
    print(f"  Credits: {credits}")
    print(f"  Balance (for EQUITY): {balance}")
    
except Account.DoesNotExist:
    print("Account 3000-01 not found!")

print(f"\n4. ENTITY STATUS:")
print(f"Is Active: {entity.is_active}")
print(f"Company Currency: {entity.company_currency}")

print("\nDebug complete.")