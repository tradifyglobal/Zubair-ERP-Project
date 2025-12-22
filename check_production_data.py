#!/usr/bin/env python3
"""
Check production database for trial balance data
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from accounting.models import Entity, LedgerEntry, Account, TrialBalance
from decimal import Decimal
from datetime import date

def check_production_data():
    print("=== PRODUCTION DATA CHECK ===")
    
    # Check entities
    entities = Entity.objects.all()
    print(f"Total entities: {entities.count()}")
    
    active_entity = Entity.objects.filter(is_active=True).first()
    print(f"Active entity: {active_entity}")
    
    if not active_entity:
        print("No active entity! Checking all entities:")
        for e in entities:
            print(f"  {e.id}: {e.name} (active: {e.is_active})")
        return
    
    # Check ledger entries
    entries = LedgerEntry.objects.filter(entity=active_entity).order_by('account__account_number', 'entry_date')
    print(f"\nLedger entries for {active_entity.name}: {entries.count()}")
    
    if entries.count() == 0:
        print("No ledger entries found!")
        return
    
    # Show entries by account
    account_totals = {}
    for entry in entries:
        acc_key = f"{entry.account.account_number} - {entry.account.name}"
        if acc_key not in account_totals:
            account_totals[acc_key] = {'debits': Decimal('0'), 'credits': Decimal('0')}
        
        if entry.entry_type == 'DEBIT':
            account_totals[acc_key]['debits'] += entry.amount
        else:
            account_totals[acc_key]['credits'] += entry.amount
        
        print(f"  {entry.account.account_number} {entry.account.name} | {entry.entry_type} ₹{entry.amount} | {entry.description}")
    
    # Show account summaries
    print(f"\nAccount Summaries:")
    total_debits = Decimal('0')
    total_credits = Decimal('0')
    
    for acc, totals in account_totals.items():
        net_balance = totals['debits'] - totals['credits']
        print(f"  {acc}:")
        print(f"    Total Debits: ₹{totals['debits']}")
        print(f"    Total Credits: ₹{totals['credits']}")
        print(f"    Net Balance: ₹{net_balance} {'(Dr)' if net_balance > 0 else '(Cr)' if net_balance < 0 else '(Zero)'}")
        
        total_debits += totals['debits']
        total_credits += totals['credits']
    
    print(f"\nGrand Totals:")
    print(f"  All Debits: ₹{total_debits}")
    print(f"  All Credits: ₹{total_credits}")
    print(f"  Difference: ₹{abs(total_debits - total_credits)}")
    
    # Check saved trial balances
    trial_balances = TrialBalance.objects.filter(entity=active_entity).order_by('-as_of_date')
    print(f"\nSaved Trial Balance records: {trial_balances.count()}")
    for tb in trial_balances[:3]:
        print(f"  {tb.as_of_date}: Dr ₹{tb.total_debits} | Cr ₹{tb.total_credits} | Bal: {tb.is_balanced}")

if __name__ == '__main__':
    check_production_data()