#!/usr/bin/env python3
import os, django, sys
sys.path.insert(0, '/var/www/tradifyerp')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from accounting.models import CashPaymentLine
from django.utils import timezone
from datetime import timedelta

# Get ALL payments with their details
all_payments = CashPaymentLine.objects.all().order_by('-created_at')

print(f"Total payments: {all_payments.count()}")
print("\nLast 3 payments:")
for p in all_payments[:3]:
    print(f"  ID: {p.id}")
    print(f"    Description: {p.description}")
    print(f"    Debit Amount: {p.debit_amount}")
    print(f"    Created: {p.created_at}")
    print(f"    Status: {p.status}")
    print()

# Check if there's an error in the form or view
print("Checking for test payment descriptions...")
test_payments = CashPaymentLine.objects.filter(description__icontains='test').order_by('-created_at')
print(f"Found {test_payments.count()} test payments")
for p in test_payments[:5]:
    print(f"  - {p.id}: {p.description} ({p.created_at})")
