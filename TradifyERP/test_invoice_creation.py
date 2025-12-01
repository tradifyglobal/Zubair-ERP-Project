#!/usr/bin/env python
"""Test script to create an invoice"""

import django
import os
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from ar.forms import CustomerInvoiceForm
from ar.models import CustomerInvoice
from accounting.models import Customer, Entity
from django.utils import timezone

# Get or create test data
entity = Entity.objects.filter(is_active=True).first()
customer = Customer.objects.first()

print("\n" + "="*80)
print("TESTING INVOICE CREATION")
print("="*80)

if not customer:
    print('ERROR: No customer found!')
    exit(1)

# Test form with valid data
form_data = {
    'customer': customer.id,
    'invoice_number': 'INV-20251122-001',
    'invoice_date': timezone.now().date(),
    'due_date': timezone.now().date(),
    'total_amount': Decimal('5000.00'),
    'status': 'DRAFT'
}

print("\nTesting form with data:")
for k, v in form_data.items():
    print(f"  {k}: {v}")

form = CustomerInvoiceForm(data=form_data)
print(f"\nForm is valid: {form.is_valid()}")

if not form.is_valid():
    print("\nForm errors:")
    for field, errors in form.errors.items():
        for error in errors:
            print(f"  {field}: {error}")
    exit(1)

print("\n✓ Form is valid! Saving...")
invoice = form.save(commit=False)
invoice.entity = entity
invoice.created_by = None  # Set manually for testing
invoice.save()

print(f"✓ Invoice created successfully!")
print(f"  ID: {invoice.id}")
print(f"  Invoice Number: {invoice.invoice_number}")
print(f"  Customer: {invoice.customer}")
print(f"  Total: {invoice.total_amount}")
print(f"  Status: {invoice.status}")

# Verify it's in the database
count = CustomerInvoice.objects.count()
print(f"\n✓ Total invoices in database: {count}")

print("\n" + "="*80)
print("SUCCESS!")
print("="*80 + "\n")
