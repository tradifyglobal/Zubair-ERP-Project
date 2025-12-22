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
    from accounting.models import CashPaymentLine, Entity, Account, Currency
    from datetime import date
    
    print("✅ Testing Fixed Exchange Rate Logic...")
    
    # Get required objects
    entity = Entity.objects.first()
    account = Account.objects.filter(account_number='100001').first()
    credit_account = Account.objects.filter(account_number='3000-04').first()  
    cad_currency = Currency.objects.filter(code='CAD').first()
    
    print(f"📋 Entity: {entity.name}")
    print(f"📋 Entity Currency: {entity.company_currency.code if entity.company_currency else 'None'}")
    print(f"📋 Transaction Currency: {cad_currency.code}")
    print(f"📋 Different currencies: {cad_currency != entity.company_currency}")
    
    # Test currency comparison logic
    if entity.company_currency and cad_currency != entity.company_currency:
        print("✅ Multi-currency transaction detected - should require exchange rate")
        
        # Create test payment with proper exchange rate
        test_payment = CashPaymentLine(
            entity=entity,
            date=date.today(),
            account=account,
            credit_account=credit_account,
            currency=cad_currency,
            description="Test exchange rate fix - CAD to INR",
            debit_amount=Decimal('1000.00'),  # 1000 CAD
            exchange_rate=Decimal('62.75'),    # 1 CAD = 62.75 INR  
            converted_debit_amount=Decimal('1000.00') * Decimal('62.75'),
            workflow_status='DRAFT'
        )
        
        test_payment.save()
        print(f"✅ Created test payment with ID: {test_payment.id}")
        
        # Verify saved data
        saved_payment = CashPaymentLine.objects.get(id=test_payment.id)
        print(f"\n📊 Verified Payment Data:")
        print(f"   Original Amount: {saved_payment.debit_amount} {saved_payment.currency.code}")
        print(f"   Exchange Rate: {saved_payment.exchange_rate}")
        print(f"   Converted Amount: {saved_payment.converted_debit_amount}")
        print(f"   Target Currency: {saved_payment.entity.company_currency.code}")
        
    else:
        print("❌ Same currency or no entity currency set")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()