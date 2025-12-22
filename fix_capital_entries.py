#!/usr/bin/env python3

import os
import sys
import django

sys.path.append('/var/www/tradifyerp')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from accounting.models import Entity, LedgerEntry, TrialBalance
from accounting.trial_balance import calculate_trial_balance
from datetime import date

def fix_capital_entries():
    print("=== FIXING CAPITAL ACCOUNT ENTRIES ===")
    
    testing_entity = Entity.objects.get(name="Testing")
    
    # Find the incorrect debit entry to the Capital account
    capital_entries = LedgerEntry.objects.filter(
        entity=testing_entity,
        account__account_number='3000-11',
        description='Cash Receipt: Test 1'
    ).order_by('entry_type')
    
    print("Capital account entries for 'Cash Receipt: Test 1':")
    for entry in capital_entries:
        print(f"  {entry.entry_type} ₹{entry.amount} - ID: {entry.id}")
    
    # Remove the incorrect DEBIT entry (Capital accounts should typically have credits for contributions)
    debit_entry = capital_entries.filter(entry_type='DEBIT').first()
    if debit_entry:
        print(f"\nRemoving incorrect DEBIT entry ID {debit_entry.id}")
        debit_entry.delete()
        print("✓ Deleted incorrect debit entry")
    else:
        print("No debit entry found to remove")
    
    # Recalculate trial balance
    print("\nRecalculating trial balance...")
    today = date.today()
    tb_data = calculate_trial_balance(testing_entity, today)
    
    print(f"New calculation:")
    print(f"Total debits: {tb_data['total_debits']}")
    print(f"Total credits: {tb_data['total_credits']}")
    print(f"Is balanced: {tb_data['is_balanced']}")
    
    print(f"\nAccount balances:")
    for balance in tb_data['account_balances']:
        print(f"  {balance['account_number']} {balance['account_name']}")
        print(f"    Debit: {balance['debit_balance']}")
        print(f"    Credit: {balance['credit_balance']}")
    
    # Update trial balance record
    tb_record, created = TrialBalance.objects.update_or_create(
        entity=testing_entity,
        as_of_date=today,
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
    fix_capital_entries()
    print("\n=== DONE ===")