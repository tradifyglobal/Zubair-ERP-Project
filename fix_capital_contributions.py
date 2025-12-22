from accounting.models import CashReceiptLine, BankReceiptLine, CapitalContribution

print("\n" + "="*70)
print("FIXING CAPITAL CONTRIBUTION TRACKING")
print("="*70)

# Reset the flags and trigger re-creation
print("\n1. Cash Receipt 13:")
cr13 = CashReceiptLine.objects.get(id=13)
print(f"   Posted flag: {cr13.is_capital_contribution_posted}")
print(f"   Resetting to False...")
cr13.is_capital_contribution_posted = False
cr13.save()
print(f"   ✅ Reset")

print("\n2. Bank Receipt 7:")
br7 = BankReceiptLine.objects.get(id=7)
print(f"   Posted flag: {br7.is_capital_contribution_posted}")
print(f"   Resetting to False...")
br7.is_capital_contribution_posted = False
br7.save()
print(f"   ✅ Reset")

print("\n" + "="*70)
print("MANUALLY CREATING CAPITAL CONTRIBUTIONS")
print("="*70)

# Since the receipts are already AUTHORIZED, the signal won't fire on save
# We need to manually create the capital contributions

from accounting.models import Stakeholder, Account
from decimal import Decimal

stakeholder = Stakeholder.objects.get(id=2)
capital_account = Account.objects.get(entity_id=7, account_number='3000-11')
cash_account = Account.objects.get(entity_id=7, account_number='100001')
entity_id = 7

# Get entity currency
from accounting.models import Entity
entity = Entity.objects.get(id=7)
company_currency = entity.company_currency

# Cash Receipt 13 - Contribution
print("\n1. Creating contribution from Cash Receipt 13...")
contrib1, created1 = CapitalContribution.objects.get_or_create(
    source_cash_receipt_id=13,
    defaults={
        'entity_id': entity_id,
        'stakeholder': stakeholder,
        'contribution_date': cr13.date,
        'amount': Decimal('100000.00'),
        'currency': cr13.currency,
        'currency_destination': company_currency,
        'status': 'APPROVED',
        'payment_mode': 'CASH',
        'reference_number': f'CAP-{cr13.id}',
        'is_auto_posted': True,
        'workflow_status': 'CONTRIBUTION',
        'equity_account': capital_account,
        'cash_account': cash_account
    }
)
print(f"   {'Created' if created1 else 'Already exists'}: {contrib1}")
cr13.is_capital_contribution_posted = True
cr13.save(update_fields=['is_capital_contribution_posted'])

# Bank Receipt 7 - Contribution  
print("\n2. Creating contribution from Bank Receipt 7...")
bank_account = Account.objects.get(entity_id=7, account_number='1000')
contrib2, created2 = CapitalContribution.objects.get_or_create(
    source_bank_receipt_id=7,
    defaults={
        'entity_id': entity_id,
        'stakeholder': stakeholder,
        'contribution_date': br7.date,
        'amount': Decimal('1000.00'),
        'currency': br7.currency,
        'currency_destination': company_currency,
        'status': 'APPROVED',
        'payment_mode': 'BANK',
        'reference_number': f'CAP-{br7.id}',
        'is_auto_posted': True,
        'workflow_status': 'CONTRIBUTION',
        'equity_account': capital_account,
        'payment_bank_account': bank_account
    }
)
print(f"   {'Created' if created2 else 'Already exists'}: {contrib2}")
br7.is_capital_contribution_posted = True
br7.save(update_fields=['is_capital_contribution_posted'])

# Cash Payment 15 - Withdrawal
print("\n3. Creating withdrawal from Cash Payment 15...")
cp15 = CashPaymentLine.objects.get(id=15)
contrib3, created3 = CapitalContribution.objects.get_or_create(
    reference_number=f'WITHDRAW-CP-15',
    defaults={
        'entity_id': entity_id,
        'stakeholder': stakeholder,
        'contribution_date': cp15.date,
        'amount': Decimal('500.00'),
        'currency': cp15.currency,
        'currency_destination': company_currency,
        'status': 'APPROVED',
        'payment_mode': 'CASH',
        'is_auto_posted': True,
        'workflow_status': 'WITHDRAWAL',
        'equity_account': capital_account,
        'cash_account': cash_account
    }
)
print(f"   {'Created' if created3 else 'Already exists'}: {contrib3}")

# Bank Payment 4 - Withdrawal
print("\n4. Creating withdrawal from Bank Payment 4...")
bp4 = BankPaymentLine.objects.get(id=4)
contrib4, created4 = CapitalContribution.objects.get_or_create(
    reference_number=f'WITHDRAW-BP-4',
    defaults={
        'entity_id': entity_id,
        'stakeholder': stakeholder,
        'contribution_date': bp4.date,
        'amount': Decimal('200.00'),
        'currency': bp4.currency,
        'currency_destination': company_currency,
        'status': 'APPROVED',
        'payment_mode': 'BANK',
        'is_auto_posted': True,
        'workflow_status': 'WITHDRAWAL',
        'equity_account': capital_account,
        'payment_bank_account': bank_account
    }
)
print(f"   {'Created' if created4 else 'Already exists'}: {contrib4}")

print("\n" + "="*70)
print("VERIFICATION")
print("="*70)

total = CapitalContribution.objects.filter(equity_account=capital_account).count()
print(f"\nTotal Capital Contributions: {total}")

contributions = Decimal('0')
withdrawals = Decimal('0')

for contrib in CapitalContribution.objects.filter(equity_account=capital_account):
    if contrib.workflow_status == 'CONTRIBUTION':
        contributions += contrib.amount
        print(f"  +{contrib.amount:,.2f} {contrib.payment_mode} (#{contrib.id})")
    else:
        withdrawals += contrib.amount
        print(f"  -{contrib.amount:,.2f} {contrib.payment_mode} (#{contrib.id})")

net = contributions - withdrawals
print(f"\nNet Investment: {net:,.2f}")
print(f"Expected: 100,300.00")
print(f"Match: {'✅' if abs(net - Decimal('100300.00')) < Decimal('0.01') else '❌'}")
print("="*70)
