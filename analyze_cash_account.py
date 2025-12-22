from accounting.models import LedgerEntry
from decimal import Decimal

print("\n" + "="*70)
print("CASH ACCOUNT (100001) - DETAILED ANALYSIS")
print("="*70)

# Get only AUTHORIZED entries (DRAFT shouldn't be in ledger)
entries = LedgerEntry.objects.filter(
    account_id='100001',
    entity_id=7
).order_by('entry_date', 'id')

print(f"\nTotal Entries: {entries.count()}\n")

debits = Decimal('0')
credits = Decimal('0')

print("Entry-by-Entry Analysis:")
print("-" * 70)

for entry in entries:
    print(f"\nDate: {entry.entry_date}")
    print(f"Reference: {entry.reference_number}")
    print(f"Status: {entry.workflow_status}")
    print(f"Type: {entry.entry_type}")
    print(f"Amount: {entry.amount:,.2f}")
    
    # Expected behavior for Cash (ASSET) account:
    # - Cash Receipt (money IN): DEBIT Cash
    # - Cash Payment (money OUT): CREDIT Cash
    # - Bank transactions should NOT affect Cash account!
    
    if 'CASH-RECEIPT' in entry.reference_number:
        expected = 'DEBIT'
        correct = '✅' if entry.entry_type == expected else '❌'
        print(f"Expected: {expected} (Cash Receipt = Money IN)")
        print(f"Actual: {entry.entry_type} {correct}")
        
    elif 'CASH-PAYMENT' in entry.reference_number:
        expected = 'CREDIT'
        correct = '✅' if entry.entry_type == expected else '❌'
        print(f"Expected: {expected} (Cash Payment = Money OUT)")
        print(f"Actual: {entry.entry_type} {correct}")
        
    elif 'BANK-RECEIPT' in entry.reference_number:
        print(f"⚠️ WARNING: Bank Receipt should NOT affect Cash account 100001!")
        print(f"   Should affect BANK account instead")
        
    elif 'BANK-PAYMENT' in entry.reference_number:
        print(f"⚠️ WARNING: Bank Payment should NOT affect Cash account 100001!")
        print(f"   Should affect BANK account instead")
        
    elif 'CAP-' in entry.reference_number:
        print(f"⚠️ WARNING: Capital Contribution entries should NOT be in ledger!")
        print(f"   These are created by Cash/Bank Receipt authorization")
    
    # Track running balance
    if entry.entry_type == 'DEBIT':
        debits += entry.amount
    else:
        credits += entry.amount
    
    running_balance = debits - credits
    print(f"Running Balance: {running_balance:,.2f}")
    
    if entry.workflow_status == 'DRAFT':
        print(f"⚠️ CRITICAL: DRAFT entries should NOT be in ledger!")

print("\n" + "="*70)
print("SUMMARY")
print("="*70)
print(f"Total Debits:  {debits:>12,.2f}")
print(f"Total Credits: {credits:>12,.2f}")
print(f"Net Balance:   {(debits - credits):>12,.2f}")
print()
print("For ASSET accounts (like Cash):")
print("  - Debits INCREASE the balance (money IN)")
print("  - Credits DECREASE the balance (money OUT)")
print("  - Normal balance is DEBIT (positive)")
print()

balance = debits - credits
if balance >= 0:
    print(f"✅ Current balance: {balance:,.2f} (normal DEBIT balance)")
else:
    print(f"❌ Current balance: {balance:,.2f} (ABNORMAL CREDIT balance)")
    print("   This means you have NEGATIVE cash - impossible!")

print("\n" + "="*70)
print("CORRECT LOGIC FOR CASH ACCOUNT:")
print("="*70)
print("1. Cash Receipt (customer pays cash):")
print("   DEBIT: 100001 - Cash")
print("   CREDIT: 3000-XX - Capital Account")
print()
print("2. Cash Payment (pay cash to stakeholder):")
print("   DEBIT: 3000-XX - Capital Account")
print("   CREDIT: 100001 - Cash")
print()
print("3. Bank Receipt: Should use BANK account, NOT Cash!")
print("4. Bank Payment: Should use BANK account, NOT Cash!")
print("="*70)
