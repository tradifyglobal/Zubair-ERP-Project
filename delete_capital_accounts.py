#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings_production')
django.setup()

from accounting.models import Account

# Check what Capital accounts exist
print("=== Current Capital Accounts ===")
accounts = Account.objects.filter(account_number__startswith='3100').order_by('account_number')
for acc in accounts:
    print(f"{acc.account_number} - {acc.name} - {acc.account_type}")

print(f"\nTotal Capital accounts found: {accounts.count()}")

# Delete the accounts
print("\n=== Deleting Capital Accounts ===")
deleted_count = 0

# First delete child accounts (3100-XX)
child_accounts = Account.objects.filter(account_number__startswith='3100-')
for acc in child_accounts:
    print(f"Deleting child account: {acc.account_number} - {acc.name}")
    acc.delete()
    deleted_count += 1

# Then delete parent account (3100)
parent_account = Account.objects.filter(account_number='3100').first()
if parent_account:
    print(f"Deleting parent account: {parent_account.account_number} - {parent_account.name}")
    parent_account.delete()
    deleted_count += 1

print(f"\nTotal accounts deleted: {deleted_count}")

# Verify deletion
print("\n=== Verification - Remaining Capital Accounts ===")
remaining_accounts = Account.objects.filter(account_number__startswith='3100').order_by('account_number')
if remaining_accounts:
    for acc in remaining_accounts:
        print(f"{acc.account_number} - {acc.name} - {acc.account_type}")
else:
    print("No Capital accounts remaining - deletion successful!")