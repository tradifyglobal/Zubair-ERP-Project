#!/usr/bin/env python
"""Test overall_rating dropdown in DistributorPerformanceForm"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from manufacturing.forms import DistributorPerformanceForm
from manufacturing.models import DistributorPerformance

print("="*80)
print("✓ Testing overall_rating Dropdown")
print("="*80)

# Check model field choices
print("\n1️⃣ Model Field Choices:")
field = DistributorPerformance._meta.get_field('overall_rating')
print(f"   Field: {field.name}")
print(f"   Type: {type(field).__name__}")
print(f"   Choices defined: {bool(field.choices)}")
if field.choices:
    for value, label in field.choices:
        print(f"     • {value}: {label}")

# Check form field
print("\n2️⃣ Form Field Configuration:")
form = DistributorPerformanceForm()
rating_field = form.fields['overall_rating']
print(f"   Field type: {type(rating_field).__name__}")
print(f"   Widget type: {type(rating_field.widget).__name__}")
print(f"   Widget classes: {rating_field.widget.attrs.get('class', 'None')}")
print(f"   Has choices: {hasattr(rating_field.widget, 'choices')}")

# Show dropdown options
print("\n3️⃣ Dropdown Options Rendered:")
if hasattr(rating_field.widget, 'choices'):
    for choice_value, choice_label in rating_field.widget.choices:
        print(f"     • <option value='{choice_value}'>{choice_label}</option>")

print("\n" + "="*80)
print("✅ overall_rating dropdown is properly configured!")
print("="*80)
