from accounting.models import (
    BankProfile, Account, Entity, CapitalContribution, 
    Stakeholder, BankPaymentLine
)
from decimal import Decimal

print("\n" + "="*70)
print("BANK PROFILE CREATION & CAPITAL CONTRIBUTION TEST")
print("="*70)

# Get Test entity and bank account
entity = Entity.objects.get(id=7, code='Test')
bank_account = Account.objects.get(entity_id=7, account_number='1000')
capital_account = Account.objects.get(entity_id=7, account_number='3000-11')
stakeholder = Stakeholder.objects.get(id=2)

print(f"\n📋 Entity: {entity.name}")
print(f"🏦 Bank Account: {bank_account.account_number} - {bank_account.name}")
print(f"💼 Capital Account: {capital_account.account_number} - {capital_account.name}")

# Check if BankProfile exists for Test entity
existing_profiles = BankProfile.objects.filter(entity=entity)
print(f"\n🔍 Existing BankProfiles: {existing_profiles.count()}")
for bp in existing_profiles:
    print(f"   #{bp.id}: {bp.bank_name} - {bp.account_number}")

# Create or get a test BankProfile
bank_profile = BankProfile.objects.filter(
    entity=entity,
    bank_name="Test Bank"
).first()

if bank_profile:
    print(f"\n✅ Test BankProfile already exists:")
    print(f"   ID: {bank_profile.id}")
    print(f"   Bank: {bank_profile.bank_name}")
    print(f"   Account: {bank_profile.account_number}")
else:
    print(f"\n⚠️  Creating Test BankProfile...")
    bank_profile = BankProfile.objects.create(
        entity=entity,
        bank_name="Test Bank",
        account_number="TEST-ACC-001",
        account_holder="Fayazuddin Zubair Mohammed",
        currency=entity.company_currency,
        is_active=True
    )
    print(f"   ✅ Created BankProfile #{bank_profile.id}")
    print(f"   Bank: {bank_profile.bank_name}")
    print(f"   Account: {bank_profile.account_number}")

# Check existing capital contributions
print("\n" + "="*70)
print("EXISTING CAPITAL CONTRIBUTIONS")
print("="*70)

existing = CapitalContribution.objects.filter(
    equity_account=capital_account
).order_by('contribution_date')

print(f"\nTotal: {existing.count()} contributions\n")
for c in existing:
    symbol = '📈' if c.workflow_status == 'CONTRIBUTION' else '📉'
    print(f"{symbol} #{c.id}: {c.workflow_status} - {c.amount:,.2f} ({c.payment_mode})")

# Check if Bank Payment 4 capital contribution exists
bp4_contrib = CapitalContribution.objects.filter(
    reference_number='WITHDRAW-BP-4'
).first()

print("\n" + "="*70)
print("BANK PAYMENT 4 - CAPITAL CONTRIBUTION")
print("="*70)

if bp4_contrib:
    print(f"\n✅ Already exists:")
    print(f"   ID: {bp4_contrib.id}")
    print(f"   Amount: {bp4_contrib.amount:,.2f}")
    print(f"   Status: {bp4_contrib.workflow_status}")
else:
    print(f"\n⚠️  Not found - creating with BankProfile...")
    
    # Get Bank Payment 4
    bp4 = BankPaymentLine.objects.get(id=4)
    
    # Create capital contribution with BankProfile
    bp4_contrib = CapitalContribution.objects.create(
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
        equity_account=capital_account,
        payment_bank_account=bank_profile  # Using BankProfile now!
    )
    print(f"   ✅ Created contribution #{bp4_contrib.id}")
    print(f"   Amount: {bp4_contrib.amount:,.2f}")
    print(f"   Bank Profile: {bp4_contrib.payment_bank_account}")

# Final summary
print("\n" + "="*70)
print("INVESTMENT SUMMARY - COMPLETE")
print("="*70)

all_contributions = CapitalContribution.objects.filter(
    equity_account=capital_account
).order_by('contribution_date')

total_in = Decimal('0')
total_out = Decimal('0')

print(f"\nAll Capital Contributions ({all_contributions.count()}):\n")
for c in all_contributions:
    symbol = '📈' if c.workflow_status == 'CONTRIBUTION' else '📉'
    sign = '+' if c.workflow_status == 'CONTRIBUTION' else '-'
    print(f"{symbol} {c.contribution_date.strftime('%Y-%m-%d')} | {c.payment_mode:4} | {sign}{c.amount:>10,.2f} | {c.reference_number or 'N/A'}")
    
    if c.workflow_status == 'CONTRIBUTION':
        total_in += c.amount
    else:
        total_out += c.amount

print(f"\n{'─'*70}")
print(f"💰 Total Contributions:  {total_in:>12,.2f}")
print(f"💸 Total Withdrawals:    {total_out:>12,.2f}")
print(f"{'─'*70}")
print(f"📊 Net Investment:       {(total_in - total_out):>12,.2f}")
print(f"\n✅ Expected: 100,300.00")
match = abs((total_in - total_out) - Decimal('100300.00')) < Decimal('0.01')
print(f"{'✅ MATCH!' if match else '❌ MISMATCH!'}")
print("="*70)
