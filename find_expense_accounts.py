#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings_production')
django.setup()

from accounting.models import Account
from expenses.models import EmployeeExpenseReport

# Find accounts with the expense entries
report = EmployeeExpenseReport.objects.get(id=5)
entity = report.entity

print(f"Entity: {entity.name}")
print(f"\nAccounts with expense GL entries:")

# Find the expense accounts
for item in report.items.all():
    if item.category.expense_account:
        acc = item.category.expense_account
        print(f"\n{acc.account_number} - {acc.name}")
        print(f"  Account ID: {acc.id}")
        print(f"  URL: https://tradifyglobal.com/accounting/accounts/{acc.id}/")

# Find AP account
ap_account = Account.objects.filter(
    entity=entity,
    account_number='2100'
).first()

if ap_account:
    print(f"\n{ap_account.account_number} - {ap_account.name}")
    print(f"  Account ID: {ap_account.id}")
    print(f"  URL: https://tradifyglobal.com/accounting/accounts/{ap_account.id}/")
