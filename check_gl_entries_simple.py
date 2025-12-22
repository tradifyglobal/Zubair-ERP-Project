#!/usr/bin/env python
"""Simple script to check GL entries."""

from accounting.models import LedgerEntry

print("=" * 80)
print("GL ENTRIES BY MODULE")
print("=" * 80)

prefixes = [
    ('Sales', 'INV-'),
    ('Manufacturing', 'MFG-'),
    ('Procurement PO', 'PO-'),
    ('Procurement GR', 'GR-'),
    ('Expenses', 'EXP-'),
    ('Maintenance', 'WO-'),
]

for module, prefix in prefixes:
    count = LedgerEntry.objects.filter(reference_number__startswith=prefix).count()
    print(f"{module:20} ({prefix:5}): {count:5} entries")

print("=" * 80)
total = LedgerEntry.objects.count()
print(f"{'Total':20} {'':5}  {total:5} entries")
print("=" * 80)
