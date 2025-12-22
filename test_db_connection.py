#!/usr/bin/env python
import os
import django
import sys

# Add project to path
sys.path.insert(0, '/var/www/tradifyerp')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings_production')

try:
    django.setup()
    from django.db import connection
    cursor = connection.cursor()
    cursor.execute("SELECT 1")
    print("✅ Database connected successfully!")
    
    # Check if our exchange rate columns exist
    cursor.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_schema = 'public'
        AND table_name = 'accounting_cashpaymentline' 
        AND column_name IN ('exchange_rate', 'converted_debit_amount', 'converted_credit_amount')
    """)
    existing_columns = cursor.fetchall()
    print(f"📊 Exchange rate columns in cash payment: {[col[0] for col in existing_columns]}")
    
    # Test creating a simple CashPaymentLine with exchange rate
    from accounting.models import CashPaymentLine
    print(f"📝 CashPaymentLine model fields: {[f.name for f in CashPaymentLine._meta.fields if 'exchange' in f.name or 'converted' in f.name]}")
    
    cursor.close()
except Exception as e:
    print(f"❌ Database connection failed: {e}")
    sys.exit(1)
