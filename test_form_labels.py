#!/usr/bin/env python3
import os
import sys
import django

sys.path.insert(0, '/var/www/tradifyerp')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tradifyerp.settings')
django.setup()

from accounting.cash_forms import CashPaymentLineForm

# Create a form instance
form = CashPaymentLineForm()

# Check the labels
print("=" * 60)
print("FORM FIELD LABELS")
print("=" * 60)

print(f"form.main_account.label = '{form.main_account.label}'")
print(f"form.account.label = '{form.account.label}'")
print(f"form.main_credit_account.label = '{form.main_credit_account.label}'")
print(f"form.credit_account.label = '{form.credit_account.label}'")

# Check disabled status
print("\n" + "=" * 60)
print("FIELD DISABLED STATUS")
print("=" * 60)
print(f"form.main_account: attrs={form.main_account.widget.attrs}")
print(f"form.account: attrs={form.account.widget.attrs}")
