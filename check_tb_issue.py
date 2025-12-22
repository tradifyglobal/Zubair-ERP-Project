#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings_production')
django.setup()

from accounting.models import TrialBalance, Entity, LedgerEntry
from accounting.trial_balance import calculate_trial_balance

def check_trial_balance_issue():
    entity = Entity.objects.first()
    print(f'Entity: {entity.name}')
    
    print('\n=== EXISTING TRIAL BALANCE RECORDS ===')
    tbs = TrialBalance.objects.filter(entity=entity).order_by('-as_of_date')
    print(f'Trial Balance Records: {tbs.count()}')
    
    if tbs.exists():
        for tb in tbs[:5]:
            print(f'{tb.as_of_date} | Debits: ₹{tb.total_debits} | Credits: ₹{tb.total_credits} | Balanced: {tb.is_balanced}')
    
    print('\n=== FRESH CALCULATION TEST ===')
    from datetime import date
    try:
        tb_data = calculate_trial_balance(entity, date.today())
        print(f'Calculated Total Debits: ₹{tb_data["total_debits"]}')
        print(f'Calculated Total Credits: ₹{tb_data["total_credits"]}')
        print(f'Is Balanced: {tb_data["is_balanced"]}')
        print(f'Account Balances: {len(tb_data["account_balances"])} accounts')
        
        # Show the account balances
        if tb_data["account_balances"]:
            print('\n=== ACCOUNT BALANCES ===')
            for acc in tb_data["account_balances"][:10]:
                print(f'{acc["account_number"]} - {acc["account_name"]} | Debit: ₹{acc["debit_balance"]} | Credit: ₹{acc["credit_balance"]}')
    except Exception as e:
        print(f'Error calculating trial balance: {e}')
    
    print('\n=== LEDGER ENTRIES CHECK ===')
    entries = LedgerEntry.objects.filter(entity=entity)
    print(f'Total Ledger Entries: {entries.count()}')
    
    if entries.exists():
        print('Recent entries:')
        for entry in entries.order_by('-created_at')[:5]:
            print(f'  {entry.entry_date} | {entry.entry_type} | {entry.account.account_number} - {entry.account.name} | ₹{entry.amount}')

if __name__ == "__main__":
    check_trial_balance_issue()