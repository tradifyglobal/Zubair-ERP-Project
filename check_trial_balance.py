#!/usr/bin/env python3
"""
Check Trial Balance Status
========================

This script checks:
1. Existing trial balance records
2. GL entries that should be included
3. Current account balances
"""

import os
import sys
import django
from datetime import date

# Add the project path
sys.path.insert(0, '/var/www/tradifyerp')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from accounting.models import TrialBalance, LedgerEntry, Account, Entity
from django.db.models import Sum, Q

def check_trial_balance():
    print("🔍 TRIAL BALANCE DIAGNOSTIC")
    print("=" * 60)
    
    # Check entities
    entities = Entity.objects.filter(is_active=True)
    print(f"\n📋 Active Entities: {entities.count()}")
    for entity in entities:
        print(f"   - {entity.code}: {entity.name}")
    
    if not entities.exists():
        print("❌ No active entities found!")
        return
    
    entity = entities.first()
    print(f"\n🏢 Using Entity: {entity.code}")
    
    # Check existing trial balances
    trial_balances = TrialBalance.objects.filter(entity=entity).order_by('-as_of_date')
    print(f"\n📊 Existing Trial Balance Records: {trial_balances.count()}")
    
    if trial_balances.exists():
        print("   Last 5 records:")
        for tb in trial_balances[:5]:
            status = "✅ Balanced" if tb.is_balanced else "❌ Unbalanced"
            print(f"   - {tb.as_of_date}: DR={tb.total_debits} CR={tb.total_credits} {status}")
    else:
        print("   No trial balance records found.")
    
    # Check GL entries
    gl_entries = LedgerEntry.objects.filter(entity=entity)
    print(f"\n📖 Total GL Entries: {gl_entries.count()}")
    
    if gl_entries.exists():
        # Latest entries
        recent_entries = gl_entries.order_by('-date')[:5]
        print("   Latest 5 entries:")
        for entry in recent_entries:
            print(f"   - {entry.date}: {entry.account.name} DR={entry.debit_amount} CR={entry.credit_amount}")
        
        # Account balances
        account_balances = gl_entries.values(
            'account__account_number', 
            'account__name'
        ).annotate(
            total_debits=Sum('debit_amount'),
            total_credits=Sum('credit_amount')
        ).order_by('account__account_number')
        
        print(f"\n💰 Account Balances Summary ({account_balances.count()} accounts):")
        total_system_debits = 0
        total_system_credits = 0
        
        for bal in account_balances:
            debits = bal['total_debits'] or 0
            credits = bal['total_credits'] or 0
            net_balance = debits - credits
            
            total_system_debits += debits
            total_system_credits += credits
            
            print(f"   {bal['account__account_number']}: {bal['account__name'][:30]:<30} DR={debits:>8.2f} CR={credits:>8.2f} NET={net_balance:>8.2f}")
        
        print(f"\n🧮 SYSTEM TOTALS:")
        print(f"   Total Debits:  ₹{total_system_debits:,.2f}")
        print(f"   Total Credits: ₹{total_system_credits:,.2f}")
        print(f"   Difference:    ₹{total_system_debits - total_system_credits:,.2f}")
        
        balanced = abs(total_system_debits - total_system_credits) < 0.01
        print(f"   Status:        {'✅ BALANCED' if balanced else '❌ UNBALANCED'}")
        
    else:
        print("   No GL entries found.")
    
    # Check accounts
    accounts = Account.objects.filter(entity=entity, is_active=True)
    print(f"\n🏦 Active Accounts: {accounts.count()}")
    if accounts.exists():
        print("   Account Structure:")
        for account in accounts.order_by('account_number')[:10]:
            print(f"   - {account.account_number}: {account.name} ({account.account_type})")
        if accounts.count() > 10:
            print(f"   ... and {accounts.count() - 10} more accounts")

if __name__ == "__main__":
    check_trial_balance()