from accounting.models import Account, LedgerEntry, CashReceiptLine, CapitalContribution
from decimal import Decimal

print("\n" + "="*70)
print("CHECKING DOUBLE POSTING ISSUE - SAJAZ AHMED")
print("="*70)

# Get Sajaz Ahmed's capital account
account = Account.objects.get(id=91959)
print(f"\n📋 Account: {account.account_number} - {account.name}")

# Get Cash Receipt 14
cr14 = CashReceiptLine.objects.filter(id=14).first()
if cr14:
    print(f"\n💰 Cash Receipt 14:")
    print(f"   Date: {cr14.date}")
    print(f"   Debit Amount: {cr14.debit_amount:,.2f}")
    print(f"   Credit Amount: {cr14.credit_amount:,.2f}")
    print(f"   Status: {cr14.workflow_status}")
    print(f"   Account: {cr14.account}")
    print(f"   Credit Account: {cr14.credit_account}")

# Get Capital Contribution CAP-120
cap120 = CapitalContribution.objects.filter(reference_number='CAP-120').first()
if cap120:
    print(f"\n📊 Capital Contribution CAP-120:")
    print(f"   Date: {cap120.contribution_date}")
    print(f"   Amount: {cap120.amount:,.2f}")
    print(f"   Status: {cap120.status}")
    print(f"   Equity Account: {cap120.equity_account}")

# Get ALL ledger entries for this account on Dec 18
ledger_entries = LedgerEntry.objects.filter(
    account=account,
    entry_date__year=2025,
    entry_date__month=12,
    entry_date__day=18
).order_by('created_at')

print(f"\n" + "="*70)
print(f"LEDGER ENTRIES FOR ACCOUNT {account.account_number} (Dec 18, 2025)")
print("="*70)
print(f"\nTotal entries: {ledger_entries.count()}\n")

running_balance = Decimal('0')
for le in ledger_entries:
    print(f"🔹 #{le.id}: {le.reference_number}")
    print(f"   Date: {le.entry_date}")
    print(f"   Description: {le.description[:60]}")
    print(f"   Debit: {le.amount if le.entry_type == 'DEBIT' else Decimal('0'):>12,.2f}")
    print(f"   Credit: {le.amount if le.entry_type == 'CREDIT' else Decimal('0'):>12,.2f}")
    if le.entry_type == 'CREDIT':
        running_balance += le.amount
    else:
        running_balance -= le.amount
    print(f"   Running Balance: {running_balance:>12,.2f}")
    print(f"   Created: {le.created_at}")
    print()

print("="*70)
print("ISSUE ANALYSIS")
print("="*70)

if ledger_entries.count() > 1:
    print(f"\n⚠️  WARNING: Found {ledger_entries.count()} ledger entries for same transaction!")
    print(f"\n🔍 Root Cause:")
    print(f"   1. Cash Receipt authorization creates ledger entry")
    print(f"   2. Capital Contribution signal auto-creates CapitalContribution")
    print(f"   3. CapitalContribution save() creates ANOTHER ledger entry")
    print(f"\n💡 Solution:")
    print(f"   CapitalContribution should NOT create ledger entries")
    print(f"   It should only track investment history")
    print(f"   Ledger entries come from Cash/Bank Receipt authorization only")
else:
    print(f"\n✅ No double posting detected")

print("="*70)
