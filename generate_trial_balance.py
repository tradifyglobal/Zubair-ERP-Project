#!/usr/bin/env python
"""Generate trial balance for Test entity"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, '/var/www/tradifyerp')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings_production')
django.setup()

from accounting.models import Entity
from accounting.trial_balance import calculate_trial_balance, save_trial_balance
from datetime import date

# Get Test entity
entity = Entity.objects.get(code='Test')
print(f"Generating trial balance for: {entity.name} (ID: {entity.id})")

# Calculate and save
today = date.today()
tb_data = calculate_trial_balance(entity, today)

if tb_data:
    print(f"\nTrial Balance Data:")
    print(f"Total Debits: {tb_data.get('total_debits', 0)}")
    print(f"Total Credits: {tb_data.get('total_credits', 0)}")
    print(f"Is Balanced: {tb_data.get('is_balanced', False)}")
    print(f"Account Count: {len(tb_data.get('account_balances', []))}")
    
    # Save to database
    tb = save_trial_balance(entity, today, force_update=True)
    print(f"\nSaved Trial Balance ID: {tb.id}")
    print(f"As of Date: {tb.as_of_date}")
else:
    print("No trial balance data calculated")
