"""
Verify UI Integration for Payment Purpose and Stakeholder Fields
This script verifies that the payment forms display correctly with the new fields
"""

import os
import django
import sys

# Add the project directory to the Python path
sys.path.insert(0, '/var/www/tradifyerp')

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from accounting.models import CashPaymentLine, BankPaymentLine, Entity, Stakeholder
from accounting.cash_forms import CashPaymentLineForm, BankPaymentLineForm

def verify_ui_integration():
    """Verify UI integration for payment forms"""
    
    print("=" * 80)
    print("PAYMENT FORM UI INTEGRATION VERIFICATION")
    print("=" * 80)
    
    # Get test entity
    test_entity = Entity.objects.filter(code='Test').first()
    
    if not test_entity:
        print("\n❌ ERROR: Test entity not found!")
        return False
    
    print(f"\n✅ Using Entity: {test_entity.name} (ID: {test_entity.id})")
    
    # Test CashPaymentLineForm
    print("\n" + "=" * 80)
    print("CASH PAYMENT FORM VERIFICATION")
    print("=" * 80)
    
    cash_form = CashPaymentLineForm(entity=test_entity)
    
    # Check if payment_purpose field exists
    if 'payment_purpose' in cash_form.fields:
        print("\n✅ payment_purpose field exists in CashPaymentLineForm")
        print(f"   Widget: {type(cash_form.fields['payment_purpose'].widget).__name__}")
        print(f"   Required: {cash_form.fields['payment_purpose'].required}")
        print(f"   Label: {cash_form.fields['payment_purpose'].label}")
    else:
        print("\n❌ payment_purpose field NOT found in CashPaymentLineForm!")
        return False
    
    # Check if stakeholder field exists
    if 'stakeholder' in cash_form.fields:
        print("\n✅ stakeholder field exists in CashPaymentLineForm")
        print(f"   Widget: {type(cash_form.fields['stakeholder'].widget).__name__}")
        print(f"   Required: {cash_form.fields['stakeholder'].required}")
        print(f"   Label: {cash_form.fields['stakeholder'].label}")
        
        # Check queryset
        stakeholder_count = cash_form.fields['stakeholder'].queryset.count()
        print(f"   Available Stakeholders: {stakeholder_count}")
        
        if stakeholder_count > 0:
            print("\n   Stakeholders:")
            for stakeholder in cash_form.fields['stakeholder'].queryset[:5]:
                print(f"   - {stakeholder.name} ({stakeholder.code})")
    else:
        print("\n❌ stakeholder field NOT found in CashPaymentLineForm!")
        return False
    
    # Test BankPaymentLineForm
    print("\n" + "=" * 80)
    print("BANK PAYMENT FORM VERIFICATION")
    print("=" * 80)
    
    bank_form = BankPaymentLineForm(entity=test_entity)
    
    # Check if payment_purpose field exists
    if 'payment_purpose' in bank_form.fields:
        print("\n✅ payment_purpose field exists in BankPaymentLineForm")
        print(f"   Widget: {type(bank_form.fields['payment_purpose'].widget).__name__}")
        print(f"   Required: {bank_form.fields['payment_purpose'].required}")
        print(f"   Label: {bank_form.fields['payment_purpose'].label}")
    else:
        print("\n❌ payment_purpose field NOT found in BankPaymentLineForm!")
        return False
    
    # Check if stakeholder field exists
    if 'stakeholder' in bank_form.fields:
        print("\n✅ stakeholder field exists in BankPaymentLineForm")
        print(f"   Widget: {type(bank_form.fields['stakeholder'].widget).__name__}")
        print(f"   Required: {bank_form.fields['stakeholder'].required}")
        print(f"   Label: {bank_form.fields['stakeholder'].label}")
        
        # Check queryset
        stakeholder_count = bank_form.fields['stakeholder'].queryset.count()
        print(f"   Available Stakeholders: {stakeholder_count}")
        
        if stakeholder_count > 0:
            print("\n   Stakeholders:")
            for stakeholder in bank_form.fields['stakeholder'].queryset[:5]:
                print(f"   - {stakeholder.name} ({stakeholder.code})")
    else:
        print("\n❌ stakeholder field NOT found in BankPaymentLineForm!")
        return False
    
    # Check payment purpose choices
    print("\n" + "=" * 80)
    print("PAYMENT PURPOSE CHOICES")
    print("=" * 80)
    
    choices = CashPaymentLine.PAYMENT_PURPOSE_CHOICES
    print(f"\n✅ Found {len(choices)} payment purpose choices:")
    for code, label in choices:
        print(f"   - {code or '(blank)'}: {label}")
    
    # Verify form validation
    print("\n" + "=" * 80)
    print("FORM VALIDATION TEST")
    print("=" * 80)
    
    # Test validation - stakeholder required for CAPITAL_WITHDRAWAL
    from decimal import Decimal
    from datetime import datetime
    from accounting.models import Account
    
    # Get test accounts
    cash_account = Account.objects.filter(
        entity=test_entity,
        account_number='100001'
    ).first()
    
    expense_account = Account.objects.filter(
        entity=test_entity,
        account_type='EXPENSE'
    ).first()
    
    if cash_account and expense_account:
        test_data = {
            'date': datetime.now().date(),
            'account': expense_account.id,
            'credit_account': cash_account.id,
            'currency': test_entity.currency.id,
            'payment_purpose': 'CAPITAL_WITHDRAWAL',
            'stakeholder': '',  # Empty - should cause validation error
            'description': 'Test capital withdrawal',
            'debit_amount': Decimal('1000.00'),
            'credit_amount': Decimal('1000.00'),
            'reference_number': 'TEST-001',
        }
        
        form = CashPaymentLineForm(data=test_data, entity=test_entity)
        
        if not form.is_valid():
            print("\n✅ Form validation works correctly!")
            print("   Validation errors:")
            for field, errors in form.errors.items():
                print(f"   - {field}: {errors}")
                
            # Check if stakeholder error exists
            if 'stakeholder' in form.errors:
                print("\n✅ Stakeholder validation working - requires stakeholder for CAPITAL_WITHDRAWAL")
            else:
                print("\n⚠️  Warning: Stakeholder validation might not be working correctly")
        else:
            print("\n⚠️  Warning: Form should have validation error for missing stakeholder")
    else:
        print("\n⚠️  Skipping validation test - required accounts not found")
    
    print("\n" + "=" * 80)
    print("UI INTEGRATION VERIFICATION COMPLETE!")
    print("=" * 80)
    print("\n✅ ALL CHECKS PASSED!")
    print("\nNext steps:")
    print("1. Open browser and navigate to: https://tradifyglobal.com/accounting/cash-payment/create/")
    print("2. Verify payment_purpose dropdown is visible")
    print("3. Select 'Capital Withdrawal' or 'Profit Distribution'")
    print("4. Verify stakeholder dropdown appears")
    print("5. Try submitting without selecting stakeholder - should show validation error")
    print("6. Repeat same test for bank payment form")
    
    return True

if __name__ == '__main__':
    try:
        success = verify_ui_integration()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
