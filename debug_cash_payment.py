#!/usr/bin/env python
"""Debug script to check cash payment ledger entries"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings_production')
django.setup()

from accounting.models import CashPaymentLine, LedgerEntry, Account

# Get cash payment #23
cp = CashPaymentLine.objects.get(id=23)

print(f"=== Cash Payment #23 Details ===")
print(f"Payment ID: {cp.id}")
print(f"Date: {cp.date}")
print(f"Description: {cp.description}")
print(f"Debit Account ID: {cp.account_id}")
if cp.account:
    print(f"Debit Account: {cp.account.account_number} - {cp.account.name}")
print(f"Credit Account ID: {cp.credit_account_id}")
if cp.credit_account:
    print(f"Credit Account: {cp.credit_account.account_number} - {cp.credit_account.name}")
print(f"Debit Amount: {cp.debit_amount}")
print(f"Credit Amount: {cp.credit_amount}")
print(f"Workflow Status: {cp.workflow_status}")
print(f"Status: {cp.status}")

print(f"\n=== Ledger Entries for CASH-PAYMENT-23 ===")
ledger_entries = LedgerEntry.objects.filter(reference_number="CASH-PAYMENT-23").order_by('id')
print(f"Total entries found: {ledger_entries.count()}")

for le in ledger_entries:
    print(f"\nEntry ID: {le.id}")
    print(f"  Entry Type: {le.entry_type}")
    print(f"  Account ID: {le.account_id}")
    print(f"  Account: {le.account.account_number} - {le.account.name}")
    print(f"  Amount: {le.amount}")
    print(f"  Description: {le.description}")
    print(f"  Posted: {le.is_posted}")
    print(f"  Workflow Status: {le.workflow_status}")

# Check if account IDs match
if ledger_entries.count() > 1:
    accounts = set([le.account_id for le in ledger_entries])
    if len(accounts) == 1:
        print(f"\n⚠️  WARNING: All ledger entries are posting to the SAME account (ID: {accounts.pop()})")
        print("This is causing both DEBIT and CREDIT to appear in the same ledger!")
