#!/usr/bin/env python
import os
import sys
import django
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from hr.models import LeaveRequest, LeaveBalance

# Get the leave request
req = LeaveRequest.objects.filter(id=1).first()
if req:
    print(f"Updating balance for leave request #{req.id}")
    print(f"Duration: {req.duration} days")
    
    # Get the leave balance
    balance = LeaveBalance.objects.get(
        employee=req.employee,
        leave_type=req.leave_type,
        year=req.start_date.year
    )
    
    print(f"Before: Taken = {balance.taken}")
    
    # Update the balance
    balance.taken = balance.taken + Decimal(str(req.duration))
    balance.save()
    
    print(f"After: Taken = {balance.taken}")
    print(f"Available: {balance.available}")
    print("✓ Updated successfully!")
