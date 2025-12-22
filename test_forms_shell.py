from accounting.cash_forms import CashPaymentLineForm, BankPaymentLineForm
from accounting.models import Entity

# Get Test entity
test_entity = Entity.objects.filter(code='Test').first()

# Create Cash Payment form
cash_form = CashPaymentLineForm(entity=test_entity)

# Check fields
print("=" * 80)
print("Cash Payment Form Fields:")
print("=" * 80)
print("payment_purpose in fields:", 'payment_purpose' in cash_form.fields)
print("stakeholder in fields:", 'stakeholder' in cash_form.fields)

if 'payment_purpose' in cash_form.fields:
    print("\npayment_purpose details:")
    print("  Label:", cash_form.fields['payment_purpose'].label)
    print("  Required:", cash_form.fields['payment_purpose'].required)

if 'stakeholder' in cash_form.fields:
    print("\nstakeholder details:")
    print("  Label:", cash_form.fields['stakeholder'].label)
    print("  Required:", cash_form.fields['stakeholder'].required)
    print("  Queryset count:", cash_form.fields['stakeholder'].queryset.count())

# Create Bank Payment form  
bank_form = BankPaymentLineForm(entity=test_entity)

print("\n" + "=" * 80)
print("Bank Payment Form Fields:")
print("=" * 80)
print("payment_purpose in fields:", 'payment_purpose' in bank_form.fields)
print("stakeholder in fields:", 'stakeholder' in bank_form.fields)

if 'payment_purpose' in bank_form.fields:
    print("\npayment_purpose details:")
    print("  Label:", bank_form.fields['payment_purpose'].label)
    print("  Required:", bank_form.fields['payment_purpose'].required)

if 'stakeholder' in bank_form.fields:
    print("\nstakeholder details:")
    print("  Label:", bank_form.fields['stakeholder'].label)
    print("  Required:", bank_form.fields['stakeholder'].required)
    print("  Queryset count:", bank_form.fields['stakeholder'].queryset.count())

print("\n✅ Form integration verification complete!")
