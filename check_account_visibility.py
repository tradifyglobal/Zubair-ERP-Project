#!/usr/bin/env python3
"""
Check if accounts are active and why they might not show
"""
import os
import django
import sys

# Add the project directory to the Python path
sys.path.append('/var/www/tradifyerp')

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')

# Setup Django
django.setup()

# Import models
from accounting.models import Entity, Account

print("CHECKING ACCOUNT VISIBILITY ON GL DASHBOARD")
print("==========================================")

# Get Testing entity
entity = Entity.objects.get(name="Testing")

# Check Sajaz account
try:
    sajaz_account = Account.objects.get(entity=entity, account_number='3000-01')
    print(f"\nAccount: {sajaz_account.account_number} - {sajaz_account.name}")
    print(f"  Entity: {sajaz_account.entity.name}")
    print(f"  Is Active: {sajaz_account.is_active}")
    print(f"  Account Type: {sajaz_account.account_type}")
    print(f"  Parent Account: {sajaz_account.parent_account}")
    
    if not sajaz_account.is_active:
        print("\n❌ ISSUE FOUND: Account is NOT ACTIVE")
        print("   Activating account...")
        sajaz_account.is_active = True
        sajaz_account.save()
        print("   ✅ Account activated")
    else:
        print("\n✅ Account is active")
        
except Account.DoesNotExist:
    print("Account 3000-01 not found!")

# Check all accounts in Testing entity
print(f"\n2. ALL EQUITY ACCOUNTS IN TESTING ENTITY:")
equity_accounts = entity.accounts.filter(account_type='EQUITY')
print(f"Total equity accounts: {equity_accounts.count()}")

for acc in equity_accounts:
    status = "ACTIVE" if acc.is_active else "INACTIVE"
    print(f"  - {acc.account_number}: {acc.name} ({status})")

# Check dashboard accounts list logic
print(f"\n3. SIMULATING DASHBOARD ACCOUNT LIST:")
accounts = entity.accounts.all()
accounts_with_balances = []

from decimal import Decimal
from django.db.models import Sum

for account in accounts:
    debits = account.ledger_entries.filter(entry_type='DEBIT').aggregate(
        total=Sum('amount')
    )['total'] or Decimal('0.00')
    credits = account.ledger_entries.filter(entry_type='CREDIT').aggregate(
        total=Sum('amount')
    )['total'] or Decimal('0.00')
    
    is_debit_based = account.account_type in ['ASSET', 'EXPENSE']
    
    if is_debit_based:
        current_balance = debits - credits
    else:
        current_balance = credits - debits
    
    accounts_with_balances.append({
        'account': account,
        'current_balance': current_balance,
        'debits': debits,
        'credits': credits
    })

print(f"Total accounts in list: {len(accounts_with_balances)}")

# Show first 10
print(f"\nFirst 10 accounts (as shown in dashboard):")
for i, item in enumerate(accounts_with_balances[:10], 1):
    print(f"{i}. {item['account'].account_number} - {item['account'].name}")
    print(f"   Balance: {item['current_balance']} (D:{item['debits']} C:{item['credits']})")

# Check if our account is in the list
sajaz_in_list = any(item['account'].account_number == '3000-01' for item in accounts_with_balances)
print(f"\n3000-01 in accounts list: {sajaz_in_list}")

if not sajaz_in_list:
    print("⚠️ Account 3000-01 is not in the accounts list!")
else:
    # Find its position
    for i, item in enumerate(accounts_with_balances):
        if item['account'].account_number == '3000-01':
            print(f"✅ Account 3000-01 is at position {i+1} in the list")
            if i >= 10:
                print(f"   NOTE: Position {i+1} is beyond the first 10 shown in dashboard")
            break

print("\nCheck complete.")