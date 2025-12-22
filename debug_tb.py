#!/usr/bin/env python3

import os
import sys
import django

sys.path.append('/var/www/tradifyerp')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from accounting.models import Entity, LedgerEntry
from accounting.trial_balance import calculate_trial_balance
from decimal import Decimal
from django.db.models import Sum, Q
from datetime import date

def debug_trial_balance():
    print("=== DEBUG TRIAL BALANCE CALCULATION ===")
    
    testing_entity = Entity.objects.get(name="Testing")
    today = date.today()
    
    # Step 1: Get GL entries
    gl_entries = LedgerEntry.objects.filter(
        entity=testing_entity,
        entry_date__lte=today
    )
    
    print(f"GL entries found: {gl_entries.count()}")
    for entry in gl_entries:
        print(f"  {entry.account.account_number} {entry.entry_type} ₹{entry.amount}")
    
    # Step 2: Calculate account balances (original logic)
    account_balances = gl_entries.values(
        'account__id',
        'account__account_number', 
        'account__name',
        'account__account_type'
    ).annotate(
        debit_balance=Sum('amount', filter=Q(entry_type='DEBIT')),
        credit_balance=Sum('amount', filter=Q(entry_type='CREDIT'))
    ).order_by('account__account_number')
    
    print(f"\nRaw account balances from DB:")
    for balance in account_balances:
        debit_bal = balance['debit_balance'] or Decimal('0.00')
        credit_bal = balance['credit_balance'] or Decimal('0.00')
        print(f"  {balance['account__account_number']} {balance['account__name']}")
        print(f"    Raw Debits: {debit_bal}")
        print(f"    Raw Credits: {credit_bal}")
        
        # Calculate net (our logic)
        net_balance = debit_bal - credit_bal
        print(f"    Net Balance: {net_balance}")
        
        if net_balance > 0:
            print(f"    → Shows as: DEBIT ₹{net_balance}")
        elif net_balance < 0:
            print(f"    → Shows as: CREDIT ₹{abs(net_balance)}")
        else:
            print(f"    → Shows as: ZERO (skipped)")
        print()
    
    # Step 3: Use our calculate function
    print("Using calculate_trial_balance function:")
    tb_data = calculate_trial_balance(testing_entity, today)
    print(f"Total debits: {tb_data['total_debits']}")
    print(f"Total credits: {tb_data['total_credits']}")
    print(f"Account balances count: {len(tb_data['account_balances'])}")
    
    for balance in tb_data['account_balances']:
        print(f"  {balance['account_number']} {balance['account_name']}")
        print(f"    Debit: {balance['debit_balance']}")
        print(f"    Credit: {balance['credit_balance']}")

if __name__ == '__main__':
    debug_trial_balance()