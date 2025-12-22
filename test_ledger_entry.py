#!/usr/bin/env python3
"""Test ledger entry details"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings_production')
django.setup()

from accounting.models import LedgerEntry
from decimal import Decimal

def main():
    # Get the latest cash payment entry
    entry = LedgerEntry.objects.filter(description__contains='Cash Payment').last()
    
    if entry:
        print(f'=== LEDGER ENTRY DETAILS ===')
        print(f'Entry ID: {entry.id}')
        print(f'Date: {entry.entry_date}')
        print(f'Account: {entry.account.account_number} - {entry.account.name}')
        print(f'Account Type: {entry.account.account_type}')
        print(f'Entry Type: {entry.entry_type}')
        print(f'Amount: {entry.amount}')
        
        print(f'\n=== ACCOUNT DETAILS ===')
        account = entry.account
        print(f'Has Parent Account: {"Yes" if account.parent_account else "No"}')
        if account.parent_account:
            print(f'Parent Account: {account.parent_account.account_number} - {account.parent_account.name}')
            print(f'Sub Account Type: Sub Account')
        else:
            print(f'Sub Account Type: Main Account')
        
        print(f'\n=== BALANCE CALCULATION ===')
        # Calculate current balance
        entries = account.ledger_entries.filter(is_posted=True)
        debits = sum(e.amount for e in entries if e.entry_type == 'DEBIT')
        credits = sum(e.amount for e in entries if e.entry_type == 'CREDIT')
        
        is_debit_based = account.account_type in ['ASSET', 'EXPENSE']
        
        if is_debit_based:
            current_balance = debits - credits
        else:
            current_balance = credits - debits
            
        print(f'Total Debits: {debits}')
        print(f'Total Credits: {credits}')
        print(f'Current Balance: {current_balance}')
    else:
        print('No cash payment entries found')

if __name__ == '__main__':
    main()