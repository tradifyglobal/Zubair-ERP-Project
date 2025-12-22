#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings_production')
django.setup()

from expenses.models import EmployeeExpenseReport

# Get report #5
report = EmployeeExpenseReport.objects.get(id=5)
print(f"Report #{report.id} - Status: {report.status}")

# Approve all items and post to GL
items = report.items.all()
print(f"\nApproving and posting {items.count()} expense items...")

for item in items:
    print(f"\nItem #{item.id}: {item.description}")
    print(f"  Before - Status: {item.status}, Posted: {item.is_posted}")
    
    # Update status to APPROVED
    item.status = 'APPROVED'
    item.save()
    
    # Post to GL
    result = item.post_to_gl()
    print(f"  After  - Status: {item.status}, Posted: {item.is_posted}")
    print(f"  GL Posting: {'SUCCESS' if result else 'FAILED'}")

print(f"\n\nReport posting status:")
result = report.post_to_gl()
print(f"Report GL Posting: {'SUCCESS' if result else 'ALREADY POSTED' if report.is_posted else 'FAILED'}")

print("\nDone!")
