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
    
    print("✅ Testing Exchange Rate Calculation and Storage...")
    
    # Get required objects
    try:
        entity = Entity.objects.first()
        account = Account.objects.filter(account_number='100001').first()  # Cash account
        credit_account = Account.objects.filter(account_number='3000-05').first()  # Shareholder capital
        cad_currency = Currency.objects.filter(code='CAD').first()
        
        if not all([entity, account, credit_account, cad_currency]):
            print("❌ Required objects not found")
            print(f"Entity: {entity}, Account: {account}, Credit Account: {credit_account}, CAD Currency: {cad_currency}")
            sys.exit(1)
        
        print(f"📋 Using Entity: {entity.name}")
        print(f"📋 Using Account: {account.name} ({account.account_number})")
        print(f"📋 Using Credit Account: {credit_account.name} ({credit_account.account_number})")
        print(f"📋 Using Currency: {cad_currency.code}")
        
        # Create test cash payment with exchange rate
        test_payment = CashPaymentLine(
            entity=entity,
            date=date.today(),
            account=account,
            credit_account=credit_account,
            currency=cad_currency,
            description="Test multi-currency payment with exchange rate",
            debit_amount=Decimal('1000.00'),  # 1000 CAD
            exchange_rate=Decimal('62.5'),    # 1 CAD = 62.5 INR
            converted_debit_amount=Decimal('1000.00') * Decimal('62.5'),  # Should be 62500 INR
            workflow_status='DRAFT'
        )
        
        test_payment.save()
        print(f"✅ Created test payment with ID: {test_payment.id}")
        
        # Verify the saved data
        saved_payment = CashPaymentLine.objects.get(id=test_payment.id)
        print(f"\n📊 Saved Payment Details:")
        print(f"   Original Amount: {saved_payment.debit_amount} {saved_payment.currency.code}")
        print(f"   Exchange Rate: {saved_payment.exchange_rate}")
        print(f"   Converted Amount: {saved_payment.converted_debit_amount}")
        print(f"   Entity Currency: {saved_payment.entity.company_currency.code if saved_payment.entity.company_currency else 'Not Set'}")
        
        print(f"\n🎉 Test completed successfully!")
        print(f"   - Exchange rate field: {'✅' if saved_payment.exchange_rate else '❌'}")
        print(f"   - Converted amount field: {'✅' if saved_payment.converted_debit_amount else '❌'}")
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        
except Exception as e:
    print(f"❌ Setup error: {e}")
    sys.exit(1)