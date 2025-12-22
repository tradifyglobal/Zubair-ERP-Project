#!/usr/bin/env python3

import os
import sys
import django

sys.path.append('/var/www/tradifyerp')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from accounting.models import Entity, LedgerEntry, TrialBalance
from accounting.trial_balance import calculate_trial_balance
from datetime import date, timedelta

def fix_trial_balance_dates():
    print("=== FIXING TRIAL BALANCE WITH CORRECT DATE ===")
    
    testing_entity = Entity.objects.get(name="Testing")
    
    # Check what dates we have entries for
    entries = LedgerEntry.objects.filter(entity=testing_entity)
    print(f"All entries: {entries.count()}")
    for entry in entries:
        print(f"  Date: {entry.entry_date} | {entry.account.account_number} {entry.entry_type} ₹{entry.amount}")
    
    # Use tomorrow's date since entries are on 2025-12-17
    tomorrow = date.today() + timedelta(days=1)
    print(f"\nCalculating trial balance as of: {tomorrow}")
    
    # Calculate trial balance
    tb_data = calculate_trial_balance(testing_entity, tomorrow)
    
    print(f"\nCalculation results:")
    print(f"Total debits: {tb_data['total_debits']}")
    print(f"Total credits: {tb_data['total_credits']}")
    print(f"Is balanced: {tb_data['is_balanced']}")
    
    print(f"\nAccount balances:")
    for balance in tb_data['account_balances']:
        print(f"  {balance['account_number']} {balance['account_name']}")
        print(f"    Debit: {balance['debit_balance']}")
        print(f"    Credit: {balance['credit_balance']}")
    
    # Update trial balance record with correct date
    tb_record, created = TrialBalance.objects.update_or_create(
        entity=testing_entity,
        as_of_date=tomorrow,
        defaults={
            'total_debits': tb_data['total_debits'],
            'total_credits': tb_data['total_credits'],
            'is_balanced': tb_data['is_balanced']
        }
    )
    
    print(f"\n{'Created' if created else 'Updated'} trial balance record:")
    print(f"Date: {tb_record.as_of_date}")
    print(f"Debits: {tb_record.total_debits}")
    print(f"Credits: {tb_record.total_credits}")
    print(f"Balanced: {tb_record.is_balanced}")

if __name__ == '__main__':
    fix_trial_balance_dates()
    print("\n=== DONE ===")