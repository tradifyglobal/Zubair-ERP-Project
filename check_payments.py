#!/usr/bin/env python3
import os
import sys
import django
sys.path.insert(0, '/var/www/tradifyerp')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings_production')
django.setup()

from accounting.models import CashPaymentLine

count = CashPaymentLine.objects.count()
print(f'Total payments in database: {count}')

latest = CashPaymentLine.objects.order_by('-created_at').first()
if latest:
    print(f'Latest payment: ID={latest.id}, Date={latest.created_at}, Desc={latest.description}')
    
# Check for test payments
test_payments = CashPaymentLine.objects.filter(description__contains='CSRF').count()
print(f'CSRF test payments found: {test_payments}')
