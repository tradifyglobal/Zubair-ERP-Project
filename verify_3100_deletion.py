#!/usr/bin/env python3
"""
Verify 3100 Capital account deletion
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
from accounting.models import Account

# Check for 3100 Capital accounts
capital_3100 = Account.objects.filter(account_number='3100', account_type='EQUITY')
total_equity = Account.objects.filter(account_type='EQUITY')

print("====================================")
print("3100 CAPITAL ACCOUNT VERIFICATION")
print("====================================")
print(f"3100 Capital accounts found: {capital_3100.count()}")
print(f"Total equity accounts: {total_equity.count()}")

if capital_3100.exists():
    print("\n❌ WARNING: 3100 Capital accounts still exist:")
    for account in capital_3100:
        print(f"  - Entity: {account.entity.name}")
        print(f"    Account: {account.account_number} - {account.name}")
        print(f"    Type: {account.account_type}")
        print(f"    Ledger Entries: {account.ledger_entries.count()}")
        print(f"    Sub-accounts: {account.sub_accounts.count()}")
        print()
else:
    print("\n✅ SUCCESS: No 3100 Capital accounts found!")

print("Verification complete.")