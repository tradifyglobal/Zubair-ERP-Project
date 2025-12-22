#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings_production')
django.setup()

from accounting.models import Account, LedgerEntry
from datetime import date

# Check account 59227
try:
    account = Account.objects.get(id=59227)
    print(f"Account ID: {account.id}")
    print(f"Account Number: {account.account_number}")
    print(f"Account Name: {account.name}")
    print(f"Account Type: {account.account_type}")
    print(f"Entity: {account.entity.name}")
    
    # Check entries for this account
    entries = LedgerEntry.objects.filter(account=account).order_by('-entry_date')
    print(f"\nTotal Entries: {entries.count()}")
    
    # Check today's entries
    today = date.today()
    today_entries = entries.filter(entry_date=today)
    print(f"Entries for today ({today}): {today_entries.count()}")
    
    # Show last 10 entries
    print(f"\nLast 10 entries:")
    for entry in entries[:10]:
        print(f"  Date: {entry.entry_date}, Type: {entry.entry_type}, Amount: ${entry.amount}, Ref: {entry.reference_number}")
    
    # Check if this is an expense account
    if account.account_number.startswith('5'):
        print(f"\nThis is an expense account")
        
        # Check for recent EXP entries
        exp_entries = entries.filter(reference_number__startswith='EXP')
        print(f"Expense-related entries: {exp_entries.count()}")
        for exp in exp_entries[:5]:
            print(f"  {exp.reference_number}: ${exp.amount} on {exp.entry_date}")
            
except Account.DoesNotExist:
    print(f"Account #{59227} not found")
