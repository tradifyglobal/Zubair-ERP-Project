#!/usr/bin/env python
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings_production')
django.setup()

from accounting.models import Account, LedgerEntry
from decimal import Decimal

expense_accounts = Account.objects.filter(account_type='EXPENSE')

if not expense_accounts.exists():
    print("No EXPENSE accounts found")
else:
    print("\nEXPENSE ACCOUNTS CHECK")
    print("="*70)
    
    for account in expense_accounts[:3]:
        print("\nAccount: {} ({})".format(account.account_number, account.name))
        print("Type: {}".format(account.account_type))
        print("Opening Balance: {}".format(account.opening_balance))
        
        entries = LedgerEntry.objects.filter(account=account).order_by('entry_date', 'id')[:5]
        
        if entries:
            print("Recent Entries:")
            opening = Decimal(str(account.opening_balance or '0.00'))
            running = opening
            debits = Decimal('0.00')
            credits = Decimal('0.00')
            
            for e in entries:
                if e.entry_type == 'DEBIT':
                    debits += e.amount
                    running += e.amount
                else:
                    credits += e.amount
                    running -= e.amount
                print("  {} | {} {} | Balance: {}".format(e.entry_date, e.entry_type, e.amount, running))
            
            expected = opening + debits - credits
            print("Expected: {} + {} - {} = {}".format(opening, debits, credits, expected))
        else:
            print("No entries")

print("\nEXPENSE accounts are DEBIT-BASED:")
print("- Debits INCREASE the balance")
print("- Credits DECREASE the balance")
print("="*70)
