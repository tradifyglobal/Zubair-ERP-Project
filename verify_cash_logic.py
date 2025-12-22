from accounting.models import LedgerEntry
from decimal import Decimal

print("\n" + "="*70)
print("CASH ACCOUNT (ID: 91983) - LOGIC VERIFICATION")
print("="*70)

# Get entries for the actual Cash account
entries = LedgerEntry.objects.filter(
    account_id=91983,
    entity_id=7
).order_by('entry_date', 'id')

print(f"\nTotal Entries: {entries.count()}\n")

debits = Decimal('0')
credits = Decimal('0')
errors = []

print("TRANSACTION-BY-TRANSACTION ANALYSIS:")
print("="*70)

for i, entry in enumerate(entries, 1):
    print(f"\n[{i}] {entry.entry_date} | Ref: {entry.reference_number}")
    print(f"    Status: {entry.workflow_status}")
    print(f"    Entry: {entry.entry_type} {entry.amount:,.2f}")
    
    # Check for errors
    transaction_errors = []
    
    # Error 1: DRAFT entries shouldn't exist in ledger
    if entry.workflow_status == 'DRAFT':
        transaction_errors.append("❌ DRAFT status - should not be in ledger!")
        errors.append(f"{entry.reference_number}: DRAFT in ledger")
    
    # Error 2: Wrong DR/CR for transaction type
    if 'CASH-RECEIPT' in entry.reference_number:
        if entry.entry_type == 'DEBIT':
            print(f"    ✅ CORRECT: Cash Receipt = DEBIT Cash (money IN)")
        else:
            transaction_errors.append("❌ WRONG: Cash Receipt should DEBIT Cash!")
            errors.append(f"{entry.reference_number}: Should be DEBIT")
            
    elif 'CASH-PAYMENT' in entry.reference_number:
        if entry.entry_type == 'CREDIT':
            print(f"    ✅ CORRECT: Cash Payment = CREDIT Cash (money OUT)")
        else:
            transaction_errors.append("❌ WRONG: Cash Payment should CREDIT Cash!")
            errors.append(f"{entry.reference_number}: Should be CREDIT")
            
    elif 'BANK-RECEIPT' in entry.reference_number:
        transaction_errors.append("❌ WRONG ACCOUNT: Bank Receipt should use BANK account, not Cash!")
        errors.append(f"{entry.reference_number}: Using Cash account instead of Bank")
        
    elif 'BANK-PAYMENT' in entry.reference_number:
        transaction_errors.append("❌ WRONG ACCOUNT: Bank Payment should use BANK account, not Cash!")
        errors.append(f"{entry.reference_number}: Using Cash account instead of Bank")
        
    elif 'CAP-' in entry.reference_number:
        transaction_errors.append("❌ DUPLICATE: Capital Contribution should not create separate ledger entry!")
        errors.append(f"{entry.reference_number}: Duplicate CAP entry")
    
    # Print errors for this transaction
    for error in transaction_errors:
        print(f"    {error}")
    
    # Track balance
    if entry.entry_type == 'DEBIT':
        debits += entry.amount
    else:
        credits += entry.amount
    
    balance = debits - credits
    print(f"    Running Balance: {balance:,.2f}")

print("\n" + "="*70)
print("FINAL CALCULATION")
print("="*70)
print(f"Total Debits:  {debits:>15,.2f} (Money IN)")
print(f"Total Credits: {credits:>15,.2f} (Money OUT)")
print(f"Net Balance:   {(debits - credits):>15,.2f}")
print()

# Filter only AUTHORIZED, non-DRAFT entries
auth_entries = [e for e in entries if e.workflow_status == 'AUTHORIZED']
auth_debits = sum(e.amount for e in auth_entries if e.entry_type == 'DEBIT')
auth_credits = sum(e.amount for e in auth_entries if e.entry_type == 'CREDIT')

print("AUTHORIZED ENTRIES ONLY:")
print(f"Debits:  {auth_debits:>15,.2f}")
print(f"Credits: {auth_credits:>15,.2f}")
print(f"Balance: {(auth_debits - auth_credits):>15,.2f}")

balance = debits - credits
if balance >= 0:
    print(f"\n✅ Cash balance: {balance:,.2f} INR (DEBIT balance - normal for ASSET)")
else:
    print(f"\n❌ Cash balance: {balance:,.2f} INR (CREDIT balance - ABNORMAL!)")
    print("   Negative cash means you've spent more than you received!")

print("\n" + "="*70)
print(f"TOTAL ERRORS FOUND: {len(errors)}")
print("="*70)
if errors:
    for i, error in enumerate(errors, 1):
        print(f"{i}. {error}")
else:
    print("No errors - all transactions are correct!")

print("\n" + "="*70)
print("EXPECTED CASH ACCOUNT LOGIC:")
print("="*70)
print("✅ Cash Receipt:  DEBIT Cash, CREDIT Capital (money comes IN)")
print("✅ Cash Payment:  DEBIT Capital, CREDIT Cash (money goes OUT)")
print("❌ Bank Receipt:  Should NOT affect Cash account!")
print("❌ Bank Payment:  Should NOT affect Cash account!")
print("="*70)
