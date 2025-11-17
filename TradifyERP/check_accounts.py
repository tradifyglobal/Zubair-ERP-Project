#!/usr/bin/env python
"""
Check existing GL accounts and their balances
"""

import os
import django
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from accounting.models import Account, LedgerEntry

print("\nALL CHART OF ACCOUNTS:")
print("-" * 100)
for account in Account.objects.all().order_by('account_number'):
    # Calculate balance from GL
    entries = LedgerEntry.objects.filter(account=account)
    debit_total = sum(e.amount for e in entries if e.entry_type == 'DEBIT')
    credit_total = sum(e.amount for e in entries if e.entry_type == 'CREDIT')
    balance = debit_total - credit_total
    
    print(f"{account.account_number:6s} | {account.name:40s} | {account.account_type:10s} | Balance: ${balance:12,.2f}")

print("\n\nREVENUE ACCOUNTS (for P&L):")
print("-" * 100)
revenue_accounts = Account.objects.filter(account_type='INCOME').order_by('account_number')
total_revenue = Decimal('0')
for account in revenue_accounts:
    entries = LedgerEntry.objects.filter(account=account)
    debit_total = sum(e.amount for e in entries if e.entry_type == 'DEBIT')
    credit_total = sum(e.amount for e in entries if e.entry_type == 'CREDIT')
    balance = credit_total - debit_total  # Revenue accounts credit balance
    total_revenue += balance
    
    print(f"{account.account_number:6s} | {account.name:40s} | ${balance:12,.2f}")

print(f"\nTOTAL INCOME: ${total_revenue:,.2f}\n")
