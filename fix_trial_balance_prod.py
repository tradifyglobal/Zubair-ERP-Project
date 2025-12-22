#!/usr/bin/env python3

import os
import sys
import django
from datetime import date

# Add current directory to Python path
sys.path.append('/var/www/tradifyerp')

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')

# Setup Django
django.setup()

# Now import models
from accounting.models import Entity, TrialBalance, LedgerEntry
from accounting.trial_balance import calculate_trial_balance

def fix_trial_balance():
    print("=== FIXING TRIAL BALANCE ===")
    
    # Check database connection
    try:
        entity_count = Entity.objects.count()
        print(f"✓ Database connected - Entities: {entity_count}")
    except Exception as e:
        print(f"✗ Database error: {e}")
        return
    
    # Get active entity
    entity = Entity.objects.filter(is_active=True).first()
    if not entity:
        print("✗ No active entity found")
        return
    
    print(f"✓ Active entity: {entity.name}")
    
    # Check ledger entries
    entries_count = LedgerEntry.objects.filter(entity=entity).count()
    print(f"✓ Ledger entries: {entries_count}")
    
    if entries_count == 0:
        print("✗ No ledger entries found")
        return
    
    # Calculate current trial balance
    today = date.today()
    print(f"\nCalculating trial balance for {today}...")
    
    try:
        tb_data = calculate_trial_balance(entity, today)
        print(f"✓ Trial balance calculated:")
        print(f"  Total debits: {tb_data['total_debits']}")
        print(f"  Total credits: {tb_data['total_credits']}")
        print(f"  Is balanced: {tb_data['is_balanced']}")
        
        print(f"\nAccount balances:")
        for balance in tb_data['account_balances']:
            print(f"  {balance['account_number']} {balance['account_name']}: Dr {balance['debit_balance']}, Cr {balance['credit_balance']}")
        
        # Update or create trial balance record
        tb_record, created = TrialBalance.objects.update_or_create(
            entity=entity,
            as_of_date=today,
            defaults={
                'total_debits': tb_data['total_debits'],
                'total_credits': tb_data['total_credits'],
                'is_balanced': tb_data['is_balanced']
            }
        )
        
        action = "Created" if created else "Updated"
        print(f"\n✓ {action} trial balance record:")
        print(f"  Date: {tb_record.as_of_date}")
        print(f"  Debits: {tb_record.total_debits}")
        print(f"  Credits: {tb_record.total_credits}")
        print(f"  Balanced: {tb_record.is_balanced}")
        
    except Exception as e:
        print(f"✗ Error calculating trial balance: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    fix_trial_balance()
    print("\n=== DONE ===")