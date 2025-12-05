#!/usr/bin/env python
"""
Verify GL entries were created for sample invoices
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from accounting.models import LedgerEntry, Account
from sales.models import Invoice

# Count GL entries
gl_entries = LedgerEntry.objects.all()
print(f"\nTotal GL Entries Created: {gl_entries.count()}\n")

# Show GL entries by account
print("GL ENTRIES BY ACCOUNT:")
print("-" * 80)
for account in Account.objects.filter(account_number__in=['1000', '1200', '2110', '4100', '4200']).order_by('account_number'):
    entries = gl_entries.filter(account=account)
    total_debit = sum(e.amount for e in entries if e.entry_type == 'DEBIT')
    total_credit = sum(e.amount for e in entries if e.entry_type == 'CREDIT')
    print(f"\n{account.account_number} - {account.name}:")
    print(f"  Entries: {entries.count()}")
    print(f"  Debits:  ${total_debit:,.2f}")
    print(f"  Credits: ${total_credit:,.2f}")
    print(f"  Balance: ${(total_debit - total_credit):,.2f}")

# Show all GL entries detail
print("\n\nALL GL ENTRIES DETAIL:")
print("-" * 80)
for entry in gl_entries[:10]:
    print(f"Account {entry.account.account_number}: {entry.entry_type:6s} ${entry.amount:,.2f} | Ref: {entry.reference_number} | Date: {entry.entry_date}")

# Show invoices
print("\n\nINVOICES CREATED:")
print("-" * 80)
for inv in Invoice.objects.all().order_by('invoice_number'):
    print(f"{inv.invoice_number}: ${inv.total_amount:,.2f} | Status: {inv.status:8s} | Paid: ${inv.amount_paid:,.2f}")

print("\n")
