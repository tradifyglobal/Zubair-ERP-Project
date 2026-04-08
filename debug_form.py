#!/usr/bin/env python
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from accounting.forms_journal_voucher import JournalVoucherLineForm
from accounting.models import JournalVoucherLine

print("=" * 60)
print("JournalVoucherLineForm Meta.fields:")
print("=" * 60)
print(f"Form fields list: {JournalVoucherLineForm.Meta.fields}")
print()

print("=" * 60)
print("JournalVoucherLine Model Fields:")
print("=" * 60)
for field in JournalVoucherLine._meta.get_fields():
    print(f"  - {field.name}: {field.__class__.__name__}")
