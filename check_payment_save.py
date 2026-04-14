#!/usr/bin/env python3
import os, django, sys
sys.path.insert(0, '/var/www/tradifyerp')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from accounting.models import CashPaymentLine
from django.utils import timezone
from datetime import timedelta

# Get payments from last 2 minutes
recent_time = timezone.now() - timedelta(minutes=2)
recent_payments = CashPaymentLine.objects.filter(created_at__gte=recent_time).order_by('-id')

if recent_payments.exists():
    print(f"Found {recent_payments.count()} recent payments:")
    for p in recent_payments[:5]:
        print(f"  ID: {p.id}, Description: {p.description}, Created: {p.created_at}, Status: {p.status}")
else:
    print("No recent payments found")
    
# Also check total count
total = CashPaymentLine.objects.count()
print(f"\nTotal payments in database: {total}")
