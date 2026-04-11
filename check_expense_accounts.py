#!/usr/bin/env python
import os
import django
import sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings_production')
django.setup()

from accounting.models import Account, LedgerEntry
from decimal import Decimal

# Find all EXPENSE accounts
expense_accounts = Account.objects.filter(account_type='EXPENSE')

if not expense_accounts.exists():
    print("No EXPENSE accounts found in database")
    sys.exit(0)

print("\n" + "="*80)
print("EXPENSE ACCOUNTS VERIFICATION (Total: {})".format(expense_accounts.count()))
print("="*80 + "\n")

for account in expense_accounts[:5]:  # Check first 5
    print("Account: {} ({})".format(account.account_number, account.name))
    print("  Type: {}".format(account.account_type))
    print("  Opening Balance: {}".format(account.opening_balance))
    
    # Get ledger entries
    entries = LedgerEntry.objects.filter(account=account).order_by('entry_date', 'id')
    
    if not entries.exists():
        print("  Status: No entries\n")
        continue
    
    # Calculate balance correctly for EXPENSE (debit-based)
    opening = Decimal(str(account.opening_balance)) if account.opening_balance else Decimal('0.00')
    total_debits = Decimal('0.00')
    total_credits = Decimal('0.00')
    
    print("  Ledger Entries:")
    running_balance = opening
    for entry in entries[:10]:  # Show first 10 entries
        if entry.entry_type == 'DEBIT':
            total_debits += entry.amount
            running_balance += entry.amount  # For debit-based accounts
        else:
            total_credits += entry.amount
            running_balance -= entry.amount  # For debit-based accounts
        
        print("    {} | {:6s} {:10.2f} | Running Balance: {:10.2f}".format(
            entry.entry_date, entry.entry_type, entry.amount, running_balance))
    
    # Final balance calculation for debit-based account
    final_balance = opening + total_debits - total_credits
    print("\n  Expected Balance (debit-based formula):")
    print("    {} + {} - {} = {}".format(opening, total_debits, total_credits, final_balance))
    print()

print("="*80)
print("EXPENSE ACCOUNTS SHOULD FOLLOW DEBIT-BASED FORMULA:")
print("  Balance = Opening Balance + Debits - Credits")
print("  Debits INCREASE balance")
print("  Credits DECREASE balance")
print("="*80 + "\n")
