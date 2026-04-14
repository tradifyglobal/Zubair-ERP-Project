#!/usr/bin/env python
"""Diagnose Trial Balance Issues"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from accounting.models import LedgerEntry, Entity, TrialBalance
from accounting.trial_balance import calculate_trial_balance
from decimal import Decimal
from datetime import date

# Get first entity
entity = Entity.objects.first()
if entity:
    print("\n" + "="*90)
    print("TRIAL BALANCE DIAGNOSIS")
    print("="*90)
    print(f"Entity: {entity.name} ({entity.code})\n")
    
    # Check GL entries
    gl_all = LedgerEntry.objects.filter(entity=entity)
    gl_authorized = gl_all.exclude(workflow_status__in=['DRAFT', 'REJECTED'])
    
    print(f"GL Entry Status:")
    print(f"  Total GL Entries:      {gl_all.count()}")
    print(f"  Authorized Entries:    {gl_authorized.count()}")
    print(f"  Draft/Rejected:        {gl_all.filter(workflow_status__in=['DRAFT', 'REJECTED']).count()}")
    print()
    
    # Get latest 10 entries
    latest = gl_authorized.order_by('-entry_date', '-created_at')[:10]
    if latest.exists():
        print("Latest 10 GL Entries:")
        print(f"  {'ID':<6} {'Date':<12} {'Account':<44} {'Type':<6} {'Amount':<12} {'Status':<12}")
        print("  " + "-"*95)
        for e in latest:
            acc_name = f"{e.account.account_number} - {e.account.name}"
            print(f"  {e.id:<6} {str(e.entry_date):<12} {acc_name[:42]:<44} {e.entry_type:<6} {e.amount:>11,.2f} {e.workflow_status:<12}")
    else:
        print("No authorized GL entries found!")
    
    # Calculate trial balance
    print(f"\n{'='*90}")
    print(f"Trial Balance Calculation as of {date.today()}")
    print(f"{'='*90}\n")
    
    tb_data = calculate_trial_balance(entity, date.today())
    
    if tb_data['account_balances']:
        print(f"Summary:")
        print(f"  Total Debits:    {tb_data['total_debits']:.2f}")
        print(f"  Total Credits:   {tb_data['total_credits']:.2f}")
        print(f"  Difference:      {abs(tb_data['total_debits'] - tb_data['total_credits']):.2f}")
        print(f"  Is Balanced:     {tb_data['is_balanced']}\n")
        
        print(f"Account Balances ({len(tb_data['account_balances'])} accounts):")
        print(f"  {'Account':<46} {'Type':<12} {'Debit':<14} {'Credit':<14}")
        print("  " + "-"*95)
        for bal in tb_data['account_balances']:
            acc_name = f"{bal['account_number']} - {bal['account_name']}"
            print(f"  {acc_name[:44]:<46} {bal['account_type']:<12} {bal['debit_balance']:>13,.2f} {bal['credit_balance']:>13,.2f}")
    else:
        print("No trial balance data!")
    
    # Get DB records
    print(f"\n{'='*90}")
    print("Database Trial Balance Records")
    print(f"{'='*90}\n")
    
    tbs = TrialBalance.objects.filter(entity=entity).order_by('-as_of_date')[:10]
    if tbs.exists():
        print(f"{'Date':<12} {'Debits':<15} {'Credits':<15} {'Difference':<15} {'Status':<15}")
        print("-"*75)
        for tb in tbs:
            diff = abs(tb.total_debits - tb.total_credits)
            status = "BALANCED" if tb.is_balanced else "UNBALANCED"
            print(f"{str(tb.as_of_date):<12} {tb.total_debits:>14,.2f} {tb.total_credits:>14,.2f} {diff:>14,.2f} {status:<15}")
    else:
        print("No trial balance records found in database (may need to generate)")
    
    print()

else:
    print("No entities found!")
