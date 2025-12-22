from accounting.models import (
    BankProfile, Account, Entity, CapitalContribution, 
    Stakeholder, CashReceipt, BankReceipt, CashPayment, BankPayment
)
from decimal import Decimal

print("\n" + "="*70)
print("CAPITAL CONTRIBUTION - COMPLETE FIX")
print("="*70)

# Get entities and accounts
entity = Entity.objects.get(id=7, code='Test')
capital_account = Account.objects.get(entity_id=7, account_number='3000-11')
stakeholder = Stakeholder.objects.get(id=2)
bank_profile = BankProfile.objects.filter(entity=entity).first()

print(f"\n📋 Entity: {entity.name}")
print(f"💼 Capital Account: {capital_account.account_number}")
print(f"🏦 Bank Profile: {bank_profile.bank_name if bank_profile else 'None'}")

# Get all cash/bank transactions
cr13 = CashReceipt.objects.get(id=13)
br7 = BankReceipt.objects.get(id=7)
cp15 = CashPayment.objects.get(id=15)
bp4 = BankPayment.objects.get(id=4)

print("\n" + "="*70)
print("TRANSACTIONS")
print("="*70)
print(f"\n📥 Cash Receipt 13: {cr13.total_amount:,.2f} ({cr13.date})")
print(f"📥 Bank Receipt 7: {br7.total_amount:,.2f} ({br7.date})")
print(f"📤 Cash Payment 15: {cp15.total_amount:,.2f} ({cp15.date})")
print(f"📤 Bank Payment 4: {bp4.total_amount:,.2f} ({bp4.date})")

# Create all 4 capital contributions
print("\n" + "="*70)
print("CREATING CAPITAL CONTRIBUTIONS")
print("="*70)

contributions = [
    {'ref': 'CONTRIB-CR-13', 'trans': cr13, 'mode': 'CASH', 'type': 'CONTRIBUTION'},
    {'ref': 'CONTRIB-BR-7', 'trans': br7, 'mode': 'BANK', 'type': 'CONTRIBUTION'},
    {'ref': 'WITHDRAW-CP-15', 'trans': cp15, 'mode': 'CASH', 'type': 'WITHDRAWAL'},
    {'ref': 'WITHDRAW-BP-4', 'trans': bp4, 'mode': 'BANK', 'type': 'WITHDRAWAL'},
]

created_count = 0
existing_count = 0

for contrib_data in contributions:
    existing = CapitalContribution.objects.filter(
        reference_number=contrib_data['ref']
    ).first()
    
    if existing:
        print(f"✅ {contrib_data['ref']}: Already exists (#{existing.id})")
        existing_count += 1
    else:
        contrib = CapitalContribution.objects.create(
            entity=entity,
            stakeholder=stakeholder,
            contribution_date=contrib_data['trans'].date,
            amount=contrib_data['trans'].total_amount,
            currency=entity.company_currency,
            currency_destination=entity.company_currency,
            status='APPROVED',
            payment_mode=contrib_data['mode'],
            reference_number=contrib_data['ref'],
            is_auto_posted=True,
            workflow_status=contrib_data['type'],
            equity_account=capital_account,
            payment_bank_account=bank_profile if contrib_data['mode'] == 'BANK' else None
        )
        print(f"✅ {contrib_data['ref']}: Created (#{contrib.id})")
        created_count += 1

print(f"\nSummary: {created_count} created, {existing_count} already existed")

# Final investment summary
print("\n" + "="*70)
print("INVESTMENT SUMMARY")
print("="*70)

all_contributions = CapitalContribution.objects.filter(
    equity_account=capital_account
).order_by('contribution_date')

total_in = Decimal('0')
total_out = Decimal('0')

print(f"\nTotal Contributions: {all_contributions.count()}\n")
print(f"{'Date':<12} {'Type':<14} {'Mode':<6} {'Amount':>14} {'Reference':<20}")
print("─" * 75)

for c in all_contributions:
    symbol = '📈' if c.workflow_status == 'CONTRIBUTION' else '📉'
    sign = '+' if c.workflow_status == 'CONTRIBUTION' else '-'
    
    print(f"{symbol} {c.contribution_date.strftime('%Y-%m-%d'):<10} {c.workflow_status:<14} {c.payment_mode:<6} {sign}{c.amount:>12,.2f} {c.reference_number or 'N/A'}")
    
    if c.workflow_status == 'CONTRIBUTION':
        total_in += c.amount
    else:
        total_out += c.amount

print("\n" + "─" * 75)
print(f"💰 Total Contributions:  {total_in:>14,.2f}")
print(f"💸 Total Withdrawals:    {total_out:>14,.2f}")
print("─" * 75)
print(f"📊 Net Investment:       {(total_in - total_out):>14,.2f}")
print(f"\n🎯 Expected:             {Decimal('100300.00'):>14,.2f}")
match = abs((total_in - total_out) - Decimal('100300.00')) < Decimal('0.01')
print(f"\n{'✅ ✅ ✅ PERFECT MATCH! ✅ ✅ ✅' if match else '❌ MISMATCH!'}")
print("="*70)
