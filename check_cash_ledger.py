#!/usr/bin/env python3

import os
import sys
import django

# Add the project directory to the Python path
sys.path.append('/var/www/tradifyerp')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from accounting.models import LedgerEntry, Account

print("=== ANALYZING CASH ACCOUNT LEDGER ENTRIES ===")

# Get cash account
cash_account = Account.objects.filter(account_number='100001').first()
if not cash_account:
    print("❌ Cash account not found")
    sys.exit(1)

print(f"Cash Account: {cash_account.account_number} - {cash_account.name}")

# Get all ledger entries for cash account
entries = LedgerEntry.objects.filter(account=cash_account).order_by('created_at')

print(f"\nTotal entries: {entries.count()}")
print("\n=== ALL CASH ACCOUNT ENTRIES ===")

total_debits = 0
total_credits = 0

for entry in entries:
    print(f"Entry {entry.id}:")
    print(f"  Date: {entry.entry_date}")
    print(f"  Type: {entry.entry_type}")
    print(f"  Amount: {entry.amount:,.2f}")
    print(f"  Description: {entry.description}")
    print(f"  Reference: {entry.reference_number}")
    print(f"  Created: {entry.created_at}")
    print()
    
    if entry.entry_type == 'DEBIT':
        total_debits += float(entry.amount)
    else:
        total_credits += float(entry.amount)

print(f"💰 Total Debits: {total_debits:,.2f}")
print(f"💰 Total Credits: {total_credits:,.2f}")
print(f"💰 Cash Balance (Debits - Credits): {total_debits - total_credits:,.2f}")

print("\n=== EXPECTED VS ACTUAL ===")
print("Expected entries:")
print("1. Cash Receipt CR001: DEBIT 100,000 (increase cash)")
print("2. Cash Payment CP001: CREDIT 200,000 (decrease cash)")  
print("   Net cash should be: 100,000 - 200,000 = -100,000")
print(f"   Actual cash balance: {total_debits - total_credits:,.2f}")

print("\n=== LOOKING FOR DUPLICATE ENTRIES ===")
# Group by reference number to find duplicates
ref_counts = {}
for entry in entries:
    ref = entry.reference_number or 'No Reference'
    if ref not in ref_counts:
        ref_counts[ref] = []
    ref_counts[ref].append(entry)

for ref, entries_list in ref_counts.items():
    if len(entries_list) > 1:
        print(f"❌ Duplicate entries for reference '{ref}':")
        for entry in entries_list:
            print(f"  Entry {entry.id}: {entry.entry_type} {entry.amount}")
    else:
        print(f"✅ Single entry for reference '{ref}': {entries_list[0].entry_type} {entries_list[0].amount}")

print("\n=== CHECKING FOR CAPITAL CONTRIBUTION AUTO-ENTRIES ===")
# Check if capital contributions created duplicate ledger entries
cap_entries = [e for e in entries if 'CAP-' in (e.reference_number or '') or 'Capital contribution' in (e.description or '')]
if cap_entries:
    print("Capital contribution related entries:")
    for entry in cap_entries:
        print(f"  Entry {entry.id}: {entry.entry_type} {entry.amount} - {entry.description} (Ref: {entry.reference_number})")
else:
    print("No capital contribution auto-entries found")