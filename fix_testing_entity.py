#!/usr/bin/env python3

import os
import sys
import django

sys.path.append('/var/www/tradifyerp')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from accounting.models import Entity, TrialBalance
from accounting.trial_balance import calculate_trial_balance
from datetime import date

def fix_testing_entity():
    print("=== FIXING TESTING ENTITY TRIAL BALANCE ===")
    
    # Get Testing entity (has the data)
    testing_entity = Entity.objects.get(name="Testing")
    print(f"Entity: {testing_entity.name} (ID: {testing_entity.id})")
    
    # Calculate correct trial balance
    today = date.today()
    tb_data = calculate_trial_balance(testing_entity, today)
    
    print(f"\nCalculated trial balance:")
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
    
    # Also set Testing as active entity
    Entity.objects.all().update(is_active=False)
    testing_entity.is_active = True
    testing_entity.save()
    print(f"\n✓ Set {testing_entity.name} as active entity")

if __name__ == '__main__':
    fix_testing_entity()
    print("\n=== DONE ===")