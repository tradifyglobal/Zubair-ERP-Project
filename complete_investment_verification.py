from accounting.models import (
    BankProfile, Account, Entity, CapitalContribution, 
    Stakeholder, CashReceiptLine, BankReceiptLine, CashPaymentLine, BankPaymentLine
)
from decimal import Decimal

print("\n" + "="*70)
print("COMPLETE CAPITAL CONTRIBUTION VERIFICATION & FIX")
print("="*70)

# Get entities and accounts
entity = Entity.objects.get(id=7, code='Test')
capital_account = Account.objects.get(entity_id=7, account_number='3000-11')
stakeholder = Stakeholder.objects.get(id=2)
bank_profile = BankProfile.objects.filter(entity=entity).first()

print(f"\n📋 Entity: {entity.name}")
print(f"💼 Capital Account: {capital_account.account_number} - {capital_account.name}")
print(f"👤 Stakeholder: {stakeholder}")
print(f"🏦 Bank Profile: {bank_profile.bank_name if bank_profile else 'None'}")

# Check all transactions
print("\n" + "="*70)
print("CHECKING ALL TRANSACTIONS")
print("="*70)

cr13 = CashReceiptLine.objects.get(id=13)
print(f"\n📥 Cash Receipt 13:")
print(f"   Amount: {cr13.amount:,.2f}")
print(f"   Date: {cr13.date}")
print(f"   Posted: {cr13.is_capital_contribution_posted}")

br7 = BankReceiptLine.objects.get(id=7)
print(f"\n📥 Bank Receipt 7:")
print(f"   Amount: {br7.amount:,.2f}")
print(f"   Date: {br7.date}")
print(f"   Posted: {br7.is_capital_contribution_posted}")

cp15 = CashPaymentLine.objects.get(id=15)
print(f"\n📤 Cash Payment 15:")
print(f"   Amount: {cp15.amount:,.2f}")
print(f"   Date: {cp15.date}")

bp4 = BankPaymentLine.objects.get(id=4)
print(f"\n📤 Bank Payment 4:")
print(f"   Amount: {bp4.amount:,.2f}")
print(f"   Date: {bp4.date}")

# Check existing contributions
print("\n" + "="*70)
print("EXISTING CAPITAL CONTRIBUTIONS")
print("="*70)

existing = CapitalContribution.objects.filter(equity_account=capital_account).order_by('contribution_date')
print(f"\nTotal: {existing.count()}\n")
for c in existing:
    symbol = '📈' if c.workflow_status == 'CONTRIBUTION' else '📉'
    print(f"{symbol} #{c.id}: {c.contribution_date} | {c.workflow_status} | {c.amount:,.2f} | {c.reference_number}")

# Create missing contributions
print("\n" + "="*70)
print("CREATING MISSING CONTRIBUTIONS")
print("="*70)

contributions_to_create = [
    {
        'ref': 'CONTRIB-CR-13',
        'date': cr13.date,
        'amount': cr13.amount,
        'mode': 'CASH',
        'status': 'CONTRIBUTION',
        'desc': 'Cash Receipt 13'
    },
    {
        'ref': 'CONTRIB-BR-7',
        'date': br7.date,
        'amount': br7.amount,
        'mode': 'BANK',
        'status': 'CONTRIBUTION',
        'desc': 'Bank Receipt 7'
    }
]

for contrib_data in contributions_to_create:
    existing_contrib = CapitalContribution.objects.filter(
        reference_number=contrib_data['ref']
    ).first()
    
    if existing_contrib:
        print(f"\n✅ {contrib_data['desc']}: Already exists (#{existing_contrib.id})")
    else:
        print(f"\n⚠️  {contrib_data['desc']}: Creating...")
        contrib = CapitalContribution.objects.create(
            entity=entity,
            stakeholder=stakeholder,
            contribution_date=contrib_data['date'],
            amount=contrib_data['amount'],
            currency=entity.company_currency,
            currency_destination=entity.company_currency,
            status='APPROVED',
            payment_mode=contrib_data['mode'],
            reference_number=contrib_data['ref'],
            is_auto_posted=True,
            workflow_status=contrib_data['status'],
            equity_account=capital_account,
            payment_bank_account=bank_profile if contrib_data['mode'] == 'BANK' else None
        )
        print(f"   ✅ Created #{contrib.id}")

# Final summary
print("\n" + "="*70)
print("FINAL INVESTMENT SUMMARY")
print("="*70)

all_contributions = CapitalContribution.objects.filter(
    equity_account=capital_account
).order_by('contribution_date')

total_in = Decimal('0')
total_out = Decimal('0')

print(f"\nAll Capital Contributions ({all_contributions.count()}):\n")
print(f"{'Date':<12} {'Type':<8} {'Mode':<6} {'Amount':>12} {'Reference':<20}")
print("─" * 70)

for c in all_contributions:
    symbol = '📈' if c.workflow_status == 'CONTRIBUTION' else '📉'
    sign = '+' if c.workflow_status == 'CONTRIBUTION' else '-'
    
    print(f"{symbol} {c.contribution_date.strftime('%Y-%m-%d'):<10} {c.workflow_status:<12} {c.payment_mode:<6} {sign}{c.amount:>10,.2f} {c.reference_number or 'N/A':<20}")
    
    if c.workflow_status == 'CONTRIBUTION':
        total_in += c.amount
    else:
        total_out += c.amount

print("\n" + "─" * 70)
print(f"💰 Total Contributions:  {total_in:>12,.2f}")
print(f"💸 Total Withdrawals:    {total_out:>12,.2f}")
print("─" * 70)
print(f"📊 Net Investment:       {(total_in - total_out):>12,.2f}")
print(f"\n✅ Expected: 100,300.00")
match = abs((total_in - total_out) - Decimal('100300.00')) < Decimal('0.01')
print(f"\n{'✅ ✅ ✅ PERFECT MATCH!' if match else '❌ MISMATCH!'}")
print("="*70)
