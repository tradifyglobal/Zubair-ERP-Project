#!/usr/bin/env python
"""Simple GL Integration Test - Just check current status and create basic test data"""

from sales.models import Customer, Invoice, SalesOrder
from manufacturing.models import Product, ProductionOrder
from maintenance.models import MaintenanceAsset, MaintenanceTask, WorkOrder
from accounting.models import LedgerEntry, Account, Entity
from django.contrib.auth.models import User
from decimal import Decimal
from datetime import date, timedelta

print("\n" + "=" * 80)
print("GL INTEGRATION TEST - SIMPLIFIED")
print("=" * 80)

# Get entity and user
entity = Entity.objects.first()
admin = User.objects.filter(is_superuser=True).first()
print(f"Entity: {entity.name}")
print(f"User: {admin.username}\n")

# Check if GL accounts exist
print("Checking GL Accounts...")
accounts_needed = [
    ('1200', 'Accounts Receivable', 'ASSET'),
    ('1300', 'Inventory', 'ASSET'),
    ('1350', 'Finished Goods', 'ASSET'),
    ('1400', 'Work in Progress', 'ASSET'),
    ('2000', 'Accounts Payable', 'LIABILITY'),
    ('4100', 'Sales Revenue', 'INCOME'),
    ('6300', 'Maintenance Expense', 'EXPENSE'),
]

for acc_num, acc_name, acc_type in accounts_needed:
    account = Account.objects.filter(entity=entity, account_number=acc_num).first()
    if account:
        print(f"  ✓ {acc_num} - {account.name}")
    else:
        print(f"  ✗ {acc_num} - {acc_name} NOT FOUND")

# Check current GL entries
print("\n" + "=" * 80)
print("CURRENT GL ENTRIES STATUS")
print("=" * 80)

modules = [
    ('Sales', 'INV-'),
    ('Manufacturing', 'MFG-'),
    ('Procurement PO', 'PO-'),
    ('Procurement GR', 'GR-'),
    ('Expenses', 'EXP-'),
    ('Payroll', 'PAY-'),
    ('Maintenance', 'WO-'),
]

for name, prefix in modules:
    count = LedgerEntry.objects.filter(reference_number__startswith=prefix).count()
    status = "✓" if count > 0 else "○"
    print(f"{status} {name:25} ({prefix}): {count:3} entries")

print("=" * 80)
print(f"Total GL Entries: {LedgerEntry.objects.count()}\n")

# Show existing entries
print("Last 5 GL Entries:")
print("-" * 80)
for entry in LedgerEntry.objects.order_by('-created_at')[:5]:
    acc = entry.account
    print(f"{entry.entry_date} | {entry.reference_number or 'NO-REF':15} | {entry.entry_type:6} | "
          f"{acc.account_number} {acc.name:30} | ${entry.amount:>10}")

print("\n" + "=" * 80)
print("✅ CHECK COMPLETED")
print("=" * 80)
