from accounting.models import BankProfile, Account, Entity, CapitalContribution, Stakeholder, CashReceiptLine, BankReceiptLine, CashPaymentLine, BankPaymentLine
from decimal import Decimal

print("\n" + "="*70)
print("CAPITAL CONTRIBUTION - COMPLETE CREATION")
print("="*70)

entity = Entity.objects.get(id=7)
capital_account = Account.objects.get(entity_id=7, account_number='3000-11')
stakeholder = Stakeholder.objects.get(id=2)
bank_profile = BankProfile.objects.filter(entity=entity).first()

print(f"\n📋 Entity: {entity.name}")
print(f"🏦 Bank Profile: {bank_profile.bank_name if bank_profile else 'None'}")

# Get transactions
cr13 = CashReceiptLine.objects.get(id=13)
br7 = BankReceiptLine.objects.get(id=7)
cp15 = CashPaymentLine.objects.get(id=15)
bp4 = BankPaymentLine.objects.get(id=4)

print(f"\n📥 CR13: {cr13.debit_amount:,.2f} ({cr13.date})")
print(f"📥 BR7: {br7.debit_amount:,.2f} ({br7.date})")
print(f"📤 CP15: {cp15.credit_amount:,.2f} ({cp15.date})")
print(f"📤 BP4: {bp4.credit_amount:,.2f} ({bp4.date})")

# Create all contributions
print("\n" + "="*70)
print("CREATING CONTRIBUTIONS")
print("="*70)

data = [
    {'ref': 'CONTRIB-CR-13', 'date': cr13.date, 'amt': cr13.debit_amount, 'mode': 'CASH', 'type': 'CONTRIBUTION'},
    {'ref': 'CONTRIB-BR-7', 'date': br7.date, 'amt': br7.debit_amount, 'mode': 'BANK', 'type': 'CONTRIBUTION'},
    {'ref': 'WITHDRAW-CP-15', 'date': cp15.date, 'amt': cp15.credit_amount, 'mode': 'CASH', 'type': 'WITHDRAWAL'},
    {'ref': 'WITHDRAW-BP-4', 'date': bp4.date, 'amt': bp4.credit_amount, 'mode': 'BANK', 'type': 'WITHDRAWAL'},
]

for d in data:
    existing = CapitalContribution.objects.filter(reference_number=d['ref']).first()
    if existing:
        print(f"✅ {d['ref']}: Exists (#{existing.id})")
    else:
        c = CapitalContribution.objects.create(
            entity=entity,
            stakeholder=stakeholder,
            contribution_date=d['date'],
            amount=d['amt'],
            currency=entity.company_currency,
            currency_destination=entity.company_currency,
            status='APPROVED',
            payment_mode=d['mode'],
            reference_number=d['ref'],
            is_auto_posted=True,
            workflow_status=d['type'],
            equity_account=capital_account,
            payment_bank_account=bank_profile if d['mode'] == 'BANK' else None
        )
        print(f"✅ {d['ref']}: Created (#{c.id})")

# Summary
print("\n" + "="*70)
print("INVESTMENT SUMMARY")
print("="*70)

all_c = CapitalContribution.objects.filter(equity_account=capital_account).order_by('contribution_date')
total_in = sum([c.amount for c in all_c if c.workflow_status == 'CONTRIBUTION'], Decimal('0'))
total_out = sum([c.amount for c in all_c if c.workflow_status == 'WITHDRAWAL'], Decimal('0'))

print(f"\nCount: {all_c.count()}\n")
for c in all_c:
    s = '📈' if c.workflow_status == 'CONTRIBUTION' else '📉'
    print(f"{s} {c.contribution_date} | {c.workflow_status:<14} | {c.amount:>10,.2f} | {c.reference_number}")

print(f"\n{'─'*70}")
print(f"💰 Contributions:  {total_in:>12,.2f}")
print(f"💸 Withdrawals:    {total_out:>12,.2f}")
print(f"{'─'*70}")
print(f"📊 Net Investment: {(total_in - total_out):>12,.2f}")
print(f"🎯 Expected:       {Decimal('100300.00'):>12,.2f}")
match = abs((total_in - total_out) - Decimal('100300.00')) < Decimal('0.01')
print(f"\n{'✅ ✅ ✅ PERFECT MATCH! ✅ ✅ ✅' if match else '❌ MISMATCH'}")
print("="*70)
