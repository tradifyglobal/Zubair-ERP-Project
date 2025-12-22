from accounting.models import CashPaymentLine, BankReceiptLine, BankPaymentLine, Account

print("\n" + "="*70)
print("FIXING ACCOUNT SELECTIONS IN DATABASE")
print("="*70)

# Fix Cash Payment 15
print("\n1. CASH PAYMENT 15:")
print("-" * 70)
payment = CashPaymentLine.objects.get(id=15)
print(f"   Before:")
print(f"     account: {payment.account}")
print(f"     credit_account: {payment.credit_account}")

# Swap the accounts
temp = payment.account
payment.account = payment.credit_account  # Set to Capital (3000-11)
payment.credit_account = temp  # Set to Cash (100001)
payment.save()

print(f"   After:")
print(f"     account: {payment.account}")
print(f"     credit_account: {payment.credit_account}")
print(f"   ✅ Fixed!")

# Find or create a bank account for Test entity
print("\n2. FINDING/CREATING BANK ACCOUNT:")
print("-" * 70)

try:
    bank_account = Account.objects.get(
        entity_id=7,
        account_number='1000'
    )
    print(f"   ✅ Found existing: {bank_account}")
except Account.DoesNotExist:
    # Create a bank account
    bank_account = Account.objects.create(
        entity_id=7,
        account_number='1000',
        name='Bank Account',
        account_type='ASSET',
        is_active=True
    )
    print(f"   ✅ Created new: {bank_account}")

# Fix Bank Receipt 7
print("\n3. BANK RECEIPT 7:")
print("-" * 70)
br = BankReceiptLine.objects.get(id=7)
print(f"   Before:")
print(f"     account: {br.account}")
print(f"     credit_account: {br.credit_account}")

# For bank receipt:
# - account should be Capital (already correct: 3000-11)
# - credit_account should be Bank (change from Cash to Bank)
br.credit_account = bank_account
br.save()

print(f"   After:")
print(f"     account: {br.account}")
print(f"     credit_account: {br.credit_account}")
print(f"   ✅ Fixed!")

# Fix Bank Payment 4
print("\n4. BANK PAYMENT 4:")
print("-" * 70)
bp = BankPaymentLine.objects.get(id=4)
print(f"   Before:")
print(f"     account: {bp.account}")
print(f"     credit_account: {bp.credit_account if hasattr(bp, 'credit_account') and bp.credit_account else 'None'}")

# For bank payment:
# - account should be Capital (change from Cash to Capital)
# - credit_account should be Bank

# Need to get capital account
capital_account = Account.objects.get(
    entity_id=7,
    account_number='3000-11'
)

bp.account = capital_account
if hasattr(bp, 'credit_account'):
    bp.credit_account = bank_account
bp.save()

print(f"   After:")
print(f"     account: {bp.account}")
print(f"     credit_account: {bp.credit_account if hasattr(bp, 'credit_account') else 'N/A'}")
print(f"   ✅ Fixed!")

print("\n" + "="*70)
print("ALL ACCOUNT SELECTIONS FIXED!")
print("="*70)
print("\nNow ready for re-authorization with correct accounts:")
print("  Cash Payment: DEBIT Capital, CREDIT Cash")
print("  Bank Receipt: DEBIT Bank, CREDIT Capital")
print("  Bank Payment: DEBIT Capital, CREDIT Bank")
print("\nPlease re-authorize these 3 transactions:")
print("  1. Cash Payment #15")
print("  2. Bank Receipt #7")
print("  3. Bank Payment #4")
print("="*70)
