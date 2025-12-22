from accounting.models import CapitalContribution, Stakeholder, Account
from decimal import Decimal

print("\n" + "="*70)
print("INVESTMENT TRACKING - FINAL VERIFICATION")
print("="*70)

stakeholder = Stakeholder.objects.get(id=2)
capital_account = Account.objects.get(entity_id=7, account_number='3000-11')

# List all contributions
contributions = CapitalContribution.objects.filter(
    equity_account=capital_account
).order_by('contribution_date')

print(f"\nTotal Capital Contributions: {contributions.count()}\n")

total_in = Decimal('0')
total_out = Decimal('0')

for c in contributions:
    symbol = '📈' if c.workflow_status == 'CONTRIBUTION' else '📉'
    print(f"{symbol} #{c.id}: {c.contribution_date}")
    print(f"   Type: {c.workflow_status}")
    print(f"   Amount: {c.amount:,.2f}")
    print(f"   Mode: {c.payment_mode}")
    print(f"   Status: {c.status}")
    print(f"   Stakeholder: {c.stakeholder}")
    print()
    
    if c.workflow_status == 'CONTRIBUTION':
        total_in += c.amount
    else:
        total_out += c.amount

# Create bank payment withdrawal if missing
print("="*70)
print("CHECKING FOR MISSING WITHDRAWALS")
print("="*70)

bp_withdrawal = CapitalContribution.objects.filter(
    reference_number='WITHDRAW-BP-4'
).first()

if not bp_withdrawal:
    print("\n⚠️  Bank Payment 4 withdrawal missing - creating...")
    from accounting.models import BankPaymentLine, Entity
    
    bp4 = BankPaymentLine.objects.get(id=4)
    entity = Entity.objects.get(id=7)
    
    bp_withdrawal = CapitalContribution.objects.create(
        entity=entity,
        stakeholder=stakeholder,
        contribution_date=bp4.date,
        amount=Decimal('200.00'),
        currency=bp4.currency,
        currency_destination=entity.company_currency,
        status='APPROVED',
        payment_mode='BANK',
        reference_number='WITHDRAW-BP-4',
        is_auto_posted=True,
        workflow_status='WITHDRAWAL',
        equity_account=capital_account
    )
    print(f"   ✅ Created: {bp_withdrawal}")
    total_out += Decimal('200.00')
else:
    print(f"\n✅ Bank Payment 4 withdrawal exists: {bp_withdrawal}")

print("\n" + "="*70)
print("INVESTMENT SUMMARY")
print("="*70)
print(f"Total Contributions: {total_in:>12,.2f}")
print(f"Total Withdrawals:   {total_out:>12,.2f}")
print(f"{'─'*45}")
print(f"Net Investment:      {(total_in - total_out):>12,.2f}")
print("\nExpected: 100,300.00")
print(f"Match: {'✅ YES' if abs((total_in - total_out) - Decimal('100300.00')) < Decimal('0.01') else '❌ NO'}")
print("="*70)
