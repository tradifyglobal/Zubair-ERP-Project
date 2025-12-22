#!/usr/bin/env python
import os
import django
import sys

# Add project to path
sys.path.insert(0, '/var/www/tradifyerp')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings_production')

try:
    django.setup()
    from accounting.models import CashPaymentLine
    from django.db import connection
    
    print("✅ Checking Cash Payment Exchange Rate Data...")
    
    # Get all cash payments
    payments = CashPaymentLine.objects.all().order_by('-date')[:10]
    
    print(f"\n📊 Latest {len(payments)} Cash Payments:")
    print("-" * 120)
    print(f"{'ID':<5} {'Date':<12} {'Description':<25} {'Amount':<12} {'Currency':<8} {'Ex.Rate':<10} {'Conv.Debit':<12} {'Conv.Credit':<12}")
    print("-" * 120)
    
    for payment in payments:
        print(f"{payment.id:<5} {str(payment.date):<12} {str(payment.description)[:24]:<25} "
              f"{payment.debit_amount:<12} {payment.currency.code if payment.currency else 'None':<8} "
              f"{payment.exchange_rate if payment.exchange_rate else 'None':<10} "
              f"{payment.converted_debit_amount if payment.converted_debit_amount else 'None':<12} "
              f"{payment.converted_credit_amount if payment.converted_credit_amount else 'None':<12}")
    
    # Check database schema
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT column_name, data_type, column_default
            FROM information_schema.columns 
            WHERE table_name = 'accounting_cashpaymentline' 
            AND column_name IN ('exchange_rate', 'converted_debit_amount', 'converted_credit_amount')
            ORDER BY column_name;
        """)
        columns = cursor.fetchall()
        
        print(f"\n🗄️ Database Schema for Exchange Rate Fields:")
        print("-" * 60)
        for col in columns:
            print(f"Column: {col[0]}, Type: {col[1]}, Default: {col[2]}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)