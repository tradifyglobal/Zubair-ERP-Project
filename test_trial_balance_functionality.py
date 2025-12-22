#!/usr/bin/env python3
"""
Test Trial Balance Functionality
===============================
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
from accounting.trial_balance import calculate_trial_balance, save_trial_balance

def test_trial_balance():
    print("🧮 TESTING TRIAL BALANCE FUNCTIONALITY")
    print("=" * 60)
    
    # Get entity
    entity = Entity.objects.filter(is_active=True).first()
    if not entity:
        print("❌ No active entity found")
        return
    
    print(f"\n🏢 Testing with Entity: {entity.code} - {entity.name}")
    
    # Check GL entries
    gl_count = LedgerEntry.objects.filter(entity=entity).count()
    print(f"📖 Total GL Entries: {gl_count}")
    
    if gl_count == 0:
        print("⚠️  No GL entries found - trial balance will be empty")
        return
    
    # Test calculate_trial_balance function
    try:
        print("\n🔄 Calculating trial balance...")
        tb_data = calculate_trial_balance(entity, date.today())
        
        print(f"   Total Debits:  ₹{tb_data['total_debits']:,.2f}")
        print(f"   Total Credits: ₹{tb_data['total_credits']:,.2f}")
        print(f"   Is Balanced:   {'✅ YES' if tb_data['is_balanced'] else '❌ NO'}")
        print(f"   Accounts:      {len(tb_data['account_balances'])}")
        
        if tb_data['account_balances']:
            print("\n📋 Account Balances:")
            for acc in tb_data['account_balances'][:5]:  # Show first 5
                print(f"   {acc['account_number']}: {acc['account_name'][:30]:<30} DR=₹{acc['debit_balance']:>8.2f} CR=₹{acc['credit_balance']:>8.2f}")
            if len(tb_data['account_balances']) > 5:
                print(f"   ... and {len(tb_data['account_balances']) - 5} more accounts")
    
    except Exception as e:
        print(f"❌ Error calculating trial balance: {e}")
        return
    
    # Test save_trial_balance function
    try:
        print("\n💾 Saving trial balance to database...")
        trial_balance = save_trial_balance(entity, date.today(), force_update=True)
        
        print(f"   Saved Trial Balance ID: {trial_balance.id}")
        print(f"   As Of Date: {trial_balance.as_of_date}")
        print(f"   Total Debits: ₹{trial_balance.total_debits:,.2f}")
        print(f"   Total Credits: ₹{trial_balance.total_credits:,.2f}")
        print(f"   Is Balanced: {'✅ YES' if trial_balance.is_balanced else '❌ NO'}")
        
    except Exception as e:
        print(f"❌ Error saving trial balance: {e}")
        return
    
    # Check database records
    tb_count = TrialBalance.objects.filter(entity=entity).count()
    print(f"\n📊 Total Trial Balance Records in DB: {tb_count}")
    
    latest_tb = TrialBalance.objects.filter(entity=entity).order_by('-as_of_date').first()
    if latest_tb:
        print(f"   Latest TB Date: {latest_tb.as_of_date}")
        print(f"   Latest TB Debits: ₹{latest_tb.total_debits:,.2f}")
        print(f"   Latest TB Credits: ₹{latest_tb.total_credits:,.2f}")
    
    print(f"\n✅ Trial Balance functionality test completed!")
    print(f"🌐 Check the web interface: https://tradifyglobal.com/accounting/trial-balances/")

if __name__ == "__main__":
    test_trial_balance()