#!/usr/bin/env python3
"""
Analyze current ledger entries to understand trial balance issue.
"""

import os
import django
import sys

# Add the project path to sys.path
sys.path.append('F:\\ERP-Production\\Zubair-ERP-Project')

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from accounting.models import LedgerEntry, Account, Entity
from decimal import Decimal

def analyze_ledger_entries():
    """Analyze current ledger entries."""
    
    # Get the entity
    entity = Entity.objects.filter(is_active=True).first()
    if not entity:
        print("No active entity found")
        return
    
    print(f"Entity: {entity.name}")
    print("=" * 60)
    
    # Get all ledger entries
    entries = LedgerEntry.objects.filter(entity=entity).order_by('account__account_number', 'entry_date')
    
    print(f"Total Ledger Entries: {entries.count()}")
    print()
    
    if entries.count() == 0:
        print("No ledger entries found!")
        return
    
    # Group by account
    account_summary = {}
    
    for entry in entries:
        acc_num = entry.account.account_number
        acc_name = entry.account.name
        acc_key = f"{acc_num} - {acc_name}"
        
        if acc_key not in account_summary:
            account_summary[acc_key] = {
                'account': entry.account,
                'debits': [],
                'credits': [],
                'total_debits': Decimal('0.00'),
                'total_credits': Decimal('0.00')
            }
        
        if entry.entry_type == 'DEBIT':
            account_summary[acc_key]['debits'].append(entry)
            account_summary[acc_key]['total_debits'] += entry.amount
        else:
            account_summary[acc_key]['credits'].append(entry)
            account_summary[acc_key]['total_credits'] += entry.amount
    
    # Display summary
    print("LEDGER ENTRIES BY ACCOUNT:")
    print("-" * 60)
    
    grand_total_debits = Decimal('0.00')
    grand_total_credits = Decimal('0.00')
    
    for acc_key, summary in account_summary.items():
        print(f"\n{acc_key}")
        print(f"Account Type: {summary['account'].account_type}")
        
        if summary['debits']:
            print(f"  Debits ({len(summary['debits'])} entries):")
            for entry in summary['debits']:
                print(f"    {entry.entry_date}: ₹{entry.amount} - {entry.description}")
        
        if summary['credits']:
            print(f"  Credits ({len(summary['credits'])} entries):")
            for entry in summary['credits']:
                print(f"    {entry.entry_date}: ₹{entry.amount} - {entry.description}")
        
        total_debits = summary['total_debits']
        total_credits = summary['total_credits']
        net_balance = total_debits - total_credits
        
        print(f"  Total Debits: ₹{total_debits}")
        print(f"  Total Credits: ₹{total_credits}")
        print(f"  Net Balance: ₹{net_balance} {'(Debit)' if net_balance > 0 else '(Credit)' if net_balance < 0 else '(Zero)'}")
        
        grand_total_debits += total_debits
        grand_total_credits += total_credits
    
    print("\n" + "=" * 60)
    print(f"GRAND TOTALS:")
    print(f"Total Debits: ₹{grand_total_debits}")
    print(f"Total Credits: ₹{grand_total_credits}")
    print(f"Difference: ₹{abs(grand_total_debits - grand_total_credits)}")
    print(f"Status: {'BALANCED' if abs(grand_total_debits - grand_total_credits) < Decimal('0.01') else 'OUT OF BALANCE'}")

if __name__ == '__main__':
    analyze_ledger_entries()