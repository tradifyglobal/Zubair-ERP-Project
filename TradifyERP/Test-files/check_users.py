#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from hr.models import LeaveRequest

# Check the leave request
req = LeaveRequest.objects.filter(id=1).first()
if req:
    print("=" * 50)
    print("LEAVE REQUEST #1")
    print("=" * 50)
    print(f"ID: {req.id}")
    print(f"Status: {req.status}")
    print(f"Requested By ID: {req.requested_by_id}")
    print(f"Requested By: {req.requested_by}")
    if req.requested_by:
        print(f"  - Full Name: {req.requested_by.get_full_name()}")
        print(f"  - Username: {req.requested_by.username}")
    
    print()
    print(f"Approved By ID: {req.approved_by_id}")
    print(f"Approved By: {req.approved_by}")
    if req.approved_by:
        print(f"  - Full Name: {req.approved_by.get_full_name()}")
        print(f"  - Username: {req.approved_by.username}")
    print(f"Approval Date: {req.approval_date}")
