#!/usr/bin/env python
"""Test script to verify CashPositionForm includes entity field"""
import os
import sys
import django

# Navigate to parent project directory
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
sys.path.insert(0, project_root)

django.setup()

from cash_management.forms import CashPositionForm
from cash_management.models import CashPosition
from accounting.models import Entity, BankProfile, Currency

print("=" * 80)
print("CASHPOSITION FORM VERIFICATION")
print("=" * 80)

# Check form fields
form = CashPositionForm()
print("\n[1] Form Fields:")
print(f"  ✓ Fields in form: {list(form.fields.keys())}")

# Verify entity field is present
if 'entity' in form.fields:
    print("  ✓ 'entity' field is PRESENT in form")
else:
    print("  ✗ 'entity' field is MISSING from form")

# Check model Meta
print("\n[2] Model Meta:")
print(f"  Fields configured: {CashPositionForm.Meta.fields}")

# Check that entity is required
if 'entity' in form.fields and form.fields['entity'].required:
    print("  ✓ 'entity' field is required")
else:
    print("  ✗ 'entity' field is not required")

print("\n" + "=" * 80)
print("FORM VERIFICATION COMPLETE")
print("=" * 80)
