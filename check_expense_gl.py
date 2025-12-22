#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings_production')
django.setup()

from expenses.models import EmployeeExpenseReport, EmployeeExpense
from accounting.models import LedgerEntry

# Check report #5
report = EmployeeExpenseReport.objects.get(id=5)
print(f"Report ID: {report.id}")
print(f"Status: {report.status}")
print(f"Total Amount: ${report.total_amount}")
print(f"Is Posted: {report.is_posted}")

# Check expense items
items = report.items.all()
print(f"\nExpense Items: {items.count()}")
for item in items:
    print(f"\n  Item #{item.id}")
    print(f"  Category: {item.category.name}")
    print(f"  Amount: ${item.amount}")
    print(f"  Status: {item.status}")
    print(f"  Is Posted: {item.is_posted}")
    if item.category.expense_account:
        print(f"  Expense Account: {item.category.expense_account.account_number} - {item.category.expense_account.name}")
    else:
        print(f"  ERROR: No expense account configured!")

# Check for related GL entries
print(f"\n\nSearching for GL Entries...")
ref_patterns = [f'EXP-5-{item.id}' for item in items]
print(f"Looking for references: {ref_patterns}")

entries = LedgerEntry.objects.filter(reference_number__in=ref_patterns)
print(f"\nGL Entries Found: {entries.count()}")

for entry in entries:
    print(f"\n  Entry ID: {entry.id}")
    print(f"  Reference: {entry.reference_number}")
    print(f"  Account: {entry.account.account_number} - {entry.account.name}")
    print(f"  Date: {entry.entry_date}")
    print(f"  Type: {entry.entry_type}")
    print(f"  Amount: ${entry.amount}")
    print(f"  Description: {entry.description}")
    print(f"  Is Posted: {entry.is_posted}")
    print(f"  Workflow Status: {entry.workflow_status}")
