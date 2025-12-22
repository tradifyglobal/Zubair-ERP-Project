from accounting.models import Account, LedgerEntry, Entity
from decimal import Decimal
from datetime import date

print("\n" + "="*70)
print("CREATING LIABILITY TEST DATA")
print("="*70)

entity = Entity.objects.get(id=7)  # Test entity

# Step 1: Create liability accounts if they don't exist
print("\n1. CREATING/FINDING LIABILITY ACCOUNTS:")
print("-" * 70)

# Loan Payable account
try:
    loan_account = Account.objects.get(
        entity=entity,
        account_number='2000'
    )
    print(f"   Found: {loan_account}")
except Account.DoesNotExist:
    loan_account = Account.objects.create(
        entity=entity,
        account_number='2000',
        name='Loan Payable',
        account_type='LIABILITY',
        is_active=True
    )
    print(f"   Created: {loan_account}")

# Accounts Payable
try:
    ap_account = Account.objects.get(
        entity=entity,
        account_number='2100'
    )
    print(f"   Found: {ap_account}")
except Account.DoesNotExist:
    ap_account = Account.objects.create(
        entity=entity,
        account_number='2100',
        name='Accounts Payable',
        account_type='LIABILITY',
        is_active=True
    )
    print(f"   Created: {ap_account}")

# Get existing accounts
cash_account = Account.objects.get(entity=entity, account_number='100001')
bank_account = Account.objects.get(entity=entity, account_number='1000')

# Step 2: Transaction 1 - Receive Bank Loan of 50,000
print("\n2. TRANSACTION: BANK LOAN RECEIVED (50,000)")
print("-" * 70)
print("   Logic: Money comes into bank, liability increases")
print("   DEBIT: Bank (1000) - Asset increases")
print("   CREDIT: Loan Payable (2000) - Liability increases")

LedgerEntry.objects.create(
    entity=entity,
    account=bank_account,
    entry_type='DEBIT',
    amount=Decimal('50000.00'),
    description='Bank loan received',
    entry_date=date(2025, 12, 18),
    reference_number='LOAN-001',
    is_posted=True,
    workflow_status='AUTHORIZED'
)

LedgerEntry.objects.create(
    entity=entity,
    account=loan_account,
    entry_type='CREDIT',
    amount=Decimal('50000.00'),
    description='Bank loan received',
    entry_date=date(2025, 12, 18),
    reference_number='LOAN-001',
    is_posted=True,
    workflow_status='AUTHORIZED'
)
print("   ✅ Created ledger entries")

# Step 3: Transaction 2 - Pay Loan Principal of 5,000
print("\n3. TRANSACTION: LOAN PAYMENT (5,000)")
print("-" * 70)
print("   Logic: Pay back part of loan from bank account")
print("   DEBIT: Loan Payable (2000) - Liability decreases")
print("   CREDIT: Bank (1000) - Asset decreases")

LedgerEntry.objects.create(
    entity=entity,
    account=loan_account,
    entry_type='DEBIT',
    amount=Decimal('5000.00'),
    description='Loan principal payment',
    entry_date=date(2025, 12, 18),
    reference_number='LOAN-PAY-001',
    is_posted=True,
    workflow_status='AUTHORIZED'
)

LedgerEntry.objects.create(
    entity=entity,
    account=bank_account,
    entry_type='CREDIT',
    amount=Decimal('5000.00'),
    description='Loan principal payment',
    entry_date=date(2025, 12, 18),
    reference_number='LOAN-PAY-001',
    is_posted=True,
    workflow_status='AUTHORIZED'
)
print("   ✅ Created ledger entries")

# Step 4: Transaction 3 - Credit Purchase (Accounts Payable)
print("\n4. TRANSACTION: CREDIT PURCHASE (10,000)")
print("-" * 70)
print("   Logic: Buy on credit (to be paid later)")
print("   DEBIT: Cash (100001) - Asset increases (received goods)")
print("   CREDIT: Accounts Payable (2100) - Liability increases")

LedgerEntry.objects.create(
    entity=entity,
    account=cash_account,
    entry_type='DEBIT',
    amount=Decimal('10000.00'),
    description='Credit purchase of goods',
    entry_date=date(2025, 12, 18),
    reference_number='CREDIT-PURCHASE-001',
    is_posted=True,
    workflow_status='AUTHORIZED'
)

LedgerEntry.objects.create(
    entity=entity,
    account=ap_account,
    entry_type='CREDIT',
    amount=Decimal('10000.00'),
    description='Credit purchase of goods',
    entry_date=date(2025, 12, 18),
    reference_number='CREDIT-PURCHASE-001',
    is_posted=True,
    workflow_status='AUTHORIZED'
)
print("   ✅ Created ledger entries")

# Step 5: Transaction 4 - Pay Accounts Payable
print("\n5. TRANSACTION: PAY ACCOUNTS PAYABLE (3,000)")
print("-" * 70)
print("   Logic: Pay supplier from cash")
print("   DEBIT: Accounts Payable (2100) - Liability decreases")
print("   CREDIT: Cash (100001) - Asset decreases")

LedgerEntry.objects.create(
    entity=entity,
    account=ap_account,
    entry_type='DEBIT',
    amount=Decimal('3000.00'),
    description='Payment to supplier',
    entry_date=date(2025, 12, 18),
    reference_number='AP-PAY-001',
    is_posted=True,
    workflow_status='AUTHORIZED'
)

LedgerEntry.objects.create(
    entity=entity,
    account=cash_account,
    entry_type='CREDIT',
    amount=Decimal('3000.00'),
    description='Payment to supplier',
    entry_date=date(2025, 12, 18),
    reference_number='AP-PAY-001',
    is_posted=True,
    workflow_status='AUTHORIZED'
)
print("   ✅ Created ledger entries")

print("\n" + "="*70)
print("LIABILITY TEST DATA CREATED SUCCESSFULLY!")
print("="*70)
print("\nCreated 4 liability transactions:")
print("  1. Bank Loan Received: +50,000 to Bank, +50,000 to Loan Payable")
print("  2. Loan Payment: -5,000 from Loan Payable, -5,000 from Bank")
print("  3. Credit Purchase: +10,000 to Cash, +10,000 to Accounts Payable")
print("  4. AP Payment: -3,000 from Accounts Payable, -3,000 from Cash")
print("\nExpected Balances:")
print("  Loan Payable: 45,000 (50,000 - 5,000)")
print("  Accounts Payable: 7,000 (10,000 - 3,000)")
print("  Total Liabilities: 52,000")
print("="*70)
