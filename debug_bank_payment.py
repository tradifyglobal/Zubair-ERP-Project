#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from accounting.models import BankPaymentLine, Account

# Get the last bank payment
bp = BankPaymentLine.objects.latest('id')
print(f"\n=== Latest Bank Payment ===")
print(f"ID: {bp.id}")
print(f"Description: {bp.description}")
print(f"Account ID (Debit): {bp.account_id}")
print(f"Credit Account ID: {bp.credit_account_id}")
print(f"Debit Amount: {bp.debit_amount}")
print(f"Credit Amount: {bp.credit_amount}")

if bp.account:
    print(f"Debit Account (account): {bp.account.account_number} - {bp.account.account_name}")
else:
    print(f"Debit Account (account): None")

if bp.credit_account:
    print(f"Credit Account (credit_account): {bp.credit_account.account_number} - {bp.credit_account.account_name}")
else:
    print(f"Credit Account (credit_account): None")

# Check if both accounts are the same 30001
if bp.account_id and bp.credit_account_id:
    if bp.account_id == bp.credit_account_id:
        print(f"\n⚠️  WARNING: Debit and Credit accounts are the SAME (both {bp.account_id})")
    else:
        print(f"\n✓ Debit account ({bp.account_id}) differs from Credit account ({bp.credit_account_id})")
