#!/usr/bin/env python3
"""Create a cash payment directly via Django ORM"""
import sys
import os
sys.path.insert(0, '/var/www/tradifyerp')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings_production')

import django
django.setup()

from accounting.models import CashPaymentLine, Entity, Account, Currency
from django.contrib.auth.models import User
from datetime import datetime
from decimal import Decimal

print("=== Creating Payment via ORM ===")

# Get or create a user
user = User.objects.filter(username='Zubair').first() or User.objects.first()
print(f"Using user: {user.username}")

# Get entity
entity = Entity.objects.filter(is_active=True).first()
print(f"Using entity: {entity.name} (ID: {entity.id})")

# Create payment
try:
    payment = CashPaymentLine.objects.create(
        entity=entity,
        date=datetime.now().date(),
        description='✅ ORM DIRECT CREATION SUCCESS TEST',
        debit_amount=Decimal('50000.00'),
        credit_amount=Decimal('50000.00'),
        status='DRAFT',
        workflow_status='DRAFT',
    )
    print(f"✅ Payment created successfully!")
    print(f"   ID: {payment.id}")
    print(f"   Description: {payment.description}")
    print(f"   Amount: {payment.debit_amount}")
    print(f"   Created at: {payment.created_at}")
except Exception as e:
    print(f"❌ Error creating payment:")
    print(f"   {type(e).__name__}: {str(e)}")

# Verify
from accounting.models import CashPaymentLine
count = CashPaymentLine.objects.count()
latest = CashPaymentLine.objects.order_by('-id').first()
print(f"\nFinal count: {count} payments")  
if latest and 'ORM DIRECT' in latest.description:
    print("✅ CONFIRMED: ORM creation works - the issue is with the form submission!")
