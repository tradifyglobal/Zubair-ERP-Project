#!/usr/bin/env python3
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings_production')
sys.path.insert(0, '/var/www/tradifyerp/TradifyERP')

django.setup()

from accounting.models import Stakeholder
from accounting.stakeholder_forms import StakeholderForm

# Check model fields
model_fields = [f.name for f in Stakeholder._meta.get_fields()]
print("Model has start_date:", 'start_date' in model_fields)
print("Model has end_date:", 'end_date' in model_fields)

# Check form fields
form = StakeholderForm()
print("\nForm fields:", sorted(form.fields.keys()))
print("\nForm has start_date:", 'start_date' in form.fields)
print("Form has end_date:", 'end_date' in form.fields)

# Check layout
if hasattr(form.helper, 'layout'):
    print("\nLayout fields count:", len(form.helper.layout.fields))
    for i, field in enumerate(form.helper.layout.fields):
        print(f"  {i}: {field}")
