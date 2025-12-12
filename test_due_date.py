#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from accounting.models import ShareholderPaymentCommitment

# Check if due_date field exists
field_names = [f.name for f in ShareholderPaymentCommitment._meta.get_fields()]
if 'due_date' in field_names:
    print("✓ due_date field exists in ShareholderPaymentCommitment model")
    # Get field info
    due_date_field = ShareholderPaymentCommitment._meta.get_field('due_date')
    print(f"  - Type: {due_date_field.get_internal_type()}")
    print(f"  - Null: {due_date_field.null}")
    print(f"  - Blank: {due_date_field.blank}")
else:
    print("✗ due_date field NOT found in model")
    print(f"Available fields: {', '.join(field_names)}")
