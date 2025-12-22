#!/usr/bin/env python3

import os
import sys
import django

sys.path.append('/var/www/tradifyerp')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from accounting.models import Entity, LedgerEntry
from decimal import Decimal

def analyze_ledger_entries():
    print("=== LEDGER ENTRIES ANALYSIS ===")
    
    testing_entity = Entity.objects.get(name="Testing")
    entries = LedgerEntry.objects.filter(entity=testing_entity).order_by('account__account_number', 'entry_date')
    
    print(f"Entity: {testing_entity.name}")
    print(f"Total entries: {entries.count()}")
    print()
    
    # Group by account
    account_summary = {}
    
    for entry in entries:
        acc_key = f"{entry.account.account_number} - {entry.account.name}"
        if acc_key not in account_summary:
            account_summary[acc_key] = {'debits': [], 'credits': [], 'total_dr': Decimal('0'), 'total_cr': Decimal('0')}
        
        print(f"Entry: {entry.account.account_number} {entry.account.name}")
        print(f"  Type: {entry.entry_type}")
        print(f"  Amount: {entry.amount}")
        print(f"  Description: {entry.description}")
        print(f"  Date: {entry.entry_date}")
        print()
        
        if entry.entry_type == 'DEBIT':
            account_summary[acc_key]['debits'].append(entry)
            account_summary[acc_key]['total_dr'] += entry.amount
        else:
            account_summary[acc_key]['credits'].append(entry)
            account_summary[acc_key]['total_cr'] += entry.amount
    
    print("=== ACCOUNT SUMMARY ===")
    for acc, summary in account_summary.items():
        net_balance = summary['total_dr'] - summary['total_cr']
        print(f"{acc}:")
        print(f"  Total Debits: {summary['total_dr']}")
        print(f"  Total Credits: {summary['total_cr']}")
        print(f"  Net Balance: {net_balance} {'(Dr)' if net_balance > 0 else '(Cr)' if net_balance < 0 else '(Zero)'}")
        print()

if __name__ == '__main__':
    analyze_ledger_entries()