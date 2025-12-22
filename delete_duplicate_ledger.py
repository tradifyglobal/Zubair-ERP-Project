from accounting.models import LedgerEntry, Account

print("\n" + "="*70)
print("DELETING DUPLICATE LEDGER ENTRY - SAJAZ AHMED")
print("="*70)

# Get Sajaz Ahmed's capital account
account = Account.objects.get(id=91959)
print(f"\n📋 Account: {account.account_number} - {account.name}")

# Get duplicate ledger entry #441 (CAP-120)
duplicate = LedgerEntry.objects.filter(id=441, reference_number='CAP-120').first()

if duplicate:
    print(f"\n🔹 Found duplicate entry:")
    print(f"   ID: {duplicate.id}")
    print(f"   Reference: {duplicate.reference_number}")
    print(f"   Description: {duplicate.description}")
    print(f"   Amount: {duplicate.amount:,.2f}")
    print(f"   Type: {duplicate.entry_type}")
    print(f"   Date: {duplicate.entry_date}")
    
    print(f"\n⚠️  Deleting duplicate ledger entry...")
    duplicate.delete()
    print(f"   ✅ Deleted!")
else:
    print(f"\n✅ No duplicate found (already deleted or doesn't exist)")

# Verify final state
ledger_entries = LedgerEntry.objects.filter(
    account=account,
    entry_date__year=2025,
    entry_date__month=12,
    entry_date__day=18
).order_by('created_at')

print(f"\n" + "="*70)
print(f"REMAINING LEDGER ENTRIES (Dec 18, 2025)")
print("="*70)
print(f"\nTotal: {ledger_entries.count()}\n")

from decimal import Decimal
balance = Decimal('0')
for le in ledger_entries:
    if le.entry_type == 'CREDIT':
        balance += le.amount
    else:
        balance -= le.amount
    print(f"#{le.id}: {le.reference_number} | {le.entry_type} | {le.amount:>10,.2f} | Balance: {balance:>10,.2f}")

print(f"\n✅ Final Balance: {balance:,.2f}")
print(f"   Expected: 100,000.00")
print(f"   {'✅ CORRECT!' if abs(balance - Decimal('100000')) < Decimal('0.01') else '❌ STILL WRONG!'}")
print("="*70)
