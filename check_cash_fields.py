#!/usr/bin/env python3

import os
import sys
import django

# Add the project directory to the Python path
sys.path.append('/var/www/tradifyerp')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from accounting.models import CashPaymentLine

print("=== CASHPAYMENTLINE MODEL FIELDS ===")
fields = [f.name for f in CashPaymentLine._meta.fields]
print("Fields:", fields)

# Check a specific entry
cp001 = CashPaymentLine.objects.filter(reference_number='CP001').first()
if cp001:
    print(f"\n=== CP001 DETAILS ===")
    for field in fields:
        value = getattr(cp001, field, 'N/A')
        print(f"{field}: {value}")