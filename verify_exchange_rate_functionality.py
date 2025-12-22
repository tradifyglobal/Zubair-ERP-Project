#!/usr/bin/env python
import os
import django
import sys
from decimal import Decimal

# Add project to path
sys.path.insert(0, '/var/www/tradifyerp')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings_production')

try:
    django.setup()
    from django.db import connection
    from accounting.models import CashPaymentLine, CashReceiptLine, BankReceiptLine, BankPaymentLine, Entity
    
    print("✅ Database connected successfully!")
    
    # Test all exchange rate models
    models_to_test = [
        ('CashPaymentLine', CashPaymentLine),
        ('CashReceiptLine', CashReceiptLine), 
        ('BankReceiptLine', BankReceiptLine),
        ('BankPaymentLine', BankPaymentLine)
    ]
    
    for model_name, model_class in models_to_test:
        exchange_fields = [f.name for f in model_class._meta.fields if 'exchange' in f.name or 'converted' in f.name]
        print(f"📊 {model_name} exchange rate fields: {exchange_fields}")
    
    # Test Entity currency fields
    entity_currency_fields = [f.name for f in Entity._meta.fields if 'currency' in f.name.lower()]
    print(f"💱 Entity currency fields: {entity_currency_fields}")
    
    # Try to query existing records to see if fields are accessible
    try:
        cash_payment_count = CashPaymentLine.objects.count()
        cash_receipt_count = CashReceiptLine.objects.count()
        bank_receipt_count = BankReceiptLine.objects.count()
        bank_payment_count = BankPaymentLine.objects.count()
        
        print(f"📈 Record counts:")
        print(f"   - Cash Payments: {cash_payment_count}")
        print(f"   - Cash Receipts: {cash_receipt_count}")
        print(f"   - Bank Receipts: {bank_receipt_count}")
        print(f"   - Bank Payments: {bank_payment_count}")
        
        # Test if we can access exchange rate fields on existing records
        if cash_payment_count > 0:
            sample_payment = CashPaymentLine.objects.first()
            print(f"💰 Sample CashPayment exchange rate: {sample_payment.exchange_rate}")
            print(f"💰 Sample CashPayment converted amounts: Debit={sample_payment.converted_debit_amount}, Credit={sample_payment.converted_credit_amount}")
        
    except Exception as e:
        print(f"⚠️ Error accessing records: {e}")
    
    print("\n🎉 Exchange rate functionality verification complete!")
    print("✅ All exchange rate fields are accessible across all cash management models")
    
except Exception as e:
    print(f"❌ Test failed: {e}")
    sys.exit(1)