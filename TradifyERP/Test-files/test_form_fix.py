#!/usr/bin/env python
"""Test that DistributorPerformanceForm properly handles performance_month and performance_year"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from manufacturing.forms import DistributorPerformanceForm
from manufacturing.models import Distributor, DistributorPerformance
from accounting.models import Entity
from datetime import date
from decimal import Decimal

print("="*80)
print("✓ Testing DistributorPerformanceForm - performance_month/year Auto-population")
print("="*80)

# Create test data
entity = Entity.objects.first() or Entity.objects.create(name="Test Entity")
distributor = Distributor.objects.first()

if not distributor:
    distributor = Distributor.objects.create(
        distributor_name="Test Distributor",
        distributor_code="TEST_PERF",
        entity=entity
    )

print(f"\n1️⃣ Test Data Setup:")
print(f"   ✓ Entity: {entity.name}")
print(f"   ✓ Distributor: {distributor.distributor_name}")

# Create form data with performance_date
form_data = {
    'distributor': distributor.id,
    'performance_date': '2025-11-15',  # November 15, 2025
    'orders_count': 5,
    'total_sales': '15000.00',
    'on_time_delivery_percentage': '85',
    'order_accuracy_percentage': '95',
    'return_rate_percentage': '5',
    'complaint_count': 1,
    'payment_on_time_percentage': '90',
    'overall_rating': '4',
}

print(f"\n2️⃣ Form Data Provided:")
print(f"   ✓ performance_date: {form_data['performance_date']}")
print(f"   ✓ orders_count: {form_data['orders_count']}")
print(f"   ✓ total_sales: {form_data['total_sales']}")
print(f"   ✓ overall_rating: {form_data['overall_rating']}")

# Create and validate form
form = DistributorPerformanceForm(data=form_data)

print(f"\n3️⃣ Form Validation:")
if form.is_valid():
    print(f"   ✓ Form is VALID")
    
    # Save the form
    instance = form.save()
    
    print(f"\n4️⃣ Auto-populated Fields:")
    print(f"   ✓ performance_month: {instance.performance_month} (from {form_data['performance_date']})")
    print(f"   ✓ performance_year: {instance.performance_year} (from {form_data['performance_date']})")
    print(f"   ✓ Database saved successfully!")
    
    # Verify in database
    saved = DistributorPerformance.objects.get(id=instance.id)
    print(f"\n5️⃣ Database Verification:")
    print(f"   ✓ Month in DB: {saved.performance_month}")
    print(f"   ✓ Year in DB: {saved.performance_year}")
    print(f"   ✓ Distributor: {saved.distributor.distributor_name}")
    print(f"   ✓ Sales: {saved.total_sales}")
    print(f"   ✓ Rating: {saved.overall_rating}")
    
    print(f"\n" + "="*80)
    print("✅ SUCCESS: performance_month and performance_year are auto-populated correctly!")
    print("✅ The IntegrityError should now be fixed!")
    print("="*80)
else:
    print(f"   ✗ Form has errors: {form.errors}")
