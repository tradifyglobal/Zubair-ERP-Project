#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from crm.models import MaintenanceSchedule, MaintenanceVisit
from accounting.models import Entity
from sales.models import Customer

entity = Entity.objects.get(id=1)

# Check if customer 1 exists
try:
    customer = Customer.objects.get(id=1)
    print(f"Customer 1 exists: {customer.name}")
except Customer.DoesNotExist:
    print("Customer 1 DOES NOT EXIST")

# Check MaintenanceSchedules
schedules = MaintenanceSchedule.objects.filter(entity=entity)
print(f"\nTotal MaintenanceSchedules: {schedules.count()}")
for sched in schedules:
    print(f"  - {sched.schedule_name}: customer_id={sched.customer_id}")
    if sched.customer:
        print(f"    Customer: {sched.customer.name}")
    else:
        print(f"    Customer: NULL")

print("\n" + "="*50 + "\n")

# Check MaintenanceVisits
visits = MaintenanceVisit.objects.filter(entity=entity)
print(f"Total MaintenanceVisits: {visits.count()}")
for visit in visits:
    sched = visit.maintenance_schedule
    print(f"  - Visit {visit.visit_number}:")
    print(f"    Schedule: {sched.schedule_name}")
    print(f"    Customer ID: {sched.customer_id}")
    if sched.customer:
        print(f"    Customer Name: {sched.customer.name}")
    else:
        print(f"    Customer: NULL")

