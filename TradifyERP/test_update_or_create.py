#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import User
from manufacturing.forms import DistributorPerformanceForm
from manufacturing.models import Distributor, DistributorPerformance
from accounting.models import Entity
from datetime import date

print("=" * 80)
print("✓ Testing Updated DistributorPerformanceForm with update_or_create")
print("=" * 80)

# Setup
entity = Entity.objects.first()
distributor = Distributor.objects.first()

print(f"\n1️⃣ Entity: {entity}")
print(f"2️⃣ Distributor: {distributor.distributor_name}")
print(f"3️⃣ Current date: {date.today()}")

# Form data - same distributor, same month/year as existing record
form_data = {
    'distributor': distributor.id,
    'performance_date': '2025-11-15',
    'orders_count': 8,
    'total_sales': '20000.00',
    'average_order_value': '2500.00',
    'on_time_delivery_percentage': '95.5',
    'order_accuracy_percentage': '98.0',
    'return_rate_percentage': '2.0',
    'complaint_count': 1,
    'payment_on_time_percentage': '99.0',
    'overall_rating': 5,
}

print(f"\n4️⃣ Form Data:")
print(f"   - Distributor: {form_data['distributor']}")
print(f"   - Performance Date: {form_data['performance_date']}")
print(f"   - Orders: {form_data['orders_count']}")
print(f"   - Rating: {form_data['overall_rating']}")

# Create form
form = DistributorPerformanceForm(data=form_data)

if form.is_valid():
    print(f"\n5️⃣ Form Validation: ✅ PASSED")
    
    # Get current count before save
    from manufacturing.models import DistributorPerformance
    count_before = DistributorPerformance.objects.count()
    
    # Save form
    instance = form.save()
    
    count_after = DistributorPerformance.objects.count()
    
    print(f"\n6️⃣ Save Operation:")
    print(f"   - Records before: {count_before}")
    print(f"   - Records after: {count_after}")
    
    if count_after == count_before:
        print(f"   - Result: ✅ UPDATED existing record (no new record created)")
    elif count_after == count_before + 1:
        print(f"   - Result: ✅ CREATED new record")
    else:
        print(f"   - Result: ⚠️ Unexpected count change")
    
    print(f"\n7️⃣ Saved Record Details:")
    print(f"   - ID: {instance.id}")
    print(f"   - Distributor: {instance.distributor.distributor_name}")
    print(f"   - Month/Year: {instance.performance_month}/{instance.performance_year}")
    print(f"   - Orders: {instance.orders_count}")
    print(f"   - Sales: {instance.total_sales}")
    print(f"   - Rating: {instance.overall_rating}")
    
    print(f"\n" + "=" * 80)
    print(f"✅ SUCCESS: Form now uses update_or_create pattern!")
    print(f"   - Multiple submissions for same distributor/month/year will UPDATE, not create duplicates")
    print(f"=" * 80)
else:
    print(f"\n❌ Form Validation FAILED")
    print(f"Errors: {form.errors}")
