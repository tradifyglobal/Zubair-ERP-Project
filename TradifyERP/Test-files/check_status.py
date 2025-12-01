#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from hr.models import LeaveRequest, LeaveBalance

# Check the leave request
req = LeaveRequest.objects.filter(id=1).first()
if req:
    print("=" * 50)
    print("LEAVE REQUEST #1")
    print("=" * 50)
    print(f"Status: {req.status}")
    print(f"Duration: {req.duration}")
    print(f"Approved By: {req.approved_by}")
    print(f"Approval Date: {req.approval_date}")
    print()

# Check the leave balance
balance = LeaveBalance.objects.filter(id=1).first()
if balance:
    print("=" * 50)
    print("LEAVE BALANCE #1")
    print("=" * 50)
    print(f"Employee: {balance.employee}")
    print(f"Leave Type: {balance.leave_type}")
    print(f"Year: {balance.year}")
    print(f"Opening Balance: {balance.opening_balance}")
    print(f"Allocated: {balance.allocated}")
    print(f"Taken: {balance.taken}")
    print(f"Available: {balance.available}")
