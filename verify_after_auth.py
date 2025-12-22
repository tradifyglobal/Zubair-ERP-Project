from accounting.models import LedgerEntry, Account, BalanceSheet, CashReceiptLine, CashPaymentLine, BankReceiptLine, BankPaymentLine
from django.db.models import Sum, Q
from decimal import Decimal

print("\n" + "="*70)
print("VERIFICATION AFTER RE-AUTHORIZATION")
print("="*70)

# Check transaction statuses
print("\nTRANSACTION STATUSES:")
print("-" * 70)

try:
    receipt = CashReceiptLine.objects.get(id=13)
    print(f"Cash Receipt 13: {receipt.workflow_status} / {receipt.status}")
except:
    print("Cash Receipt 13: Not found")

try:
    payment = CashPaymentLine.objects.get(id=15)
    print(f"Cash Payment 15: {payment.workflow_status} / {payment.status}")
except:
    print("Cash Payment 15: Not found")

try:
    bank_receipt = BankReceiptLine.objects.get(id=7)
    print(f"Bank Receipt 7: {bank_receipt.workflow_status} / {bank_receipt.status}")
except:
    print("Bank Receipt 7: Not found")

try:
    bank_payment = BankPaymentLine.objects.get(id=4)
    print(f"Bank Payment 4: {bank_payment.workflow_status} / {bank_payment.status}")
except:
    print("Bank Payment 4: Not found")

# Check ledger entries
print("\n" + "="*70)
print("LEDGER ENTRIES FOR TEST ENTITY")
print("="*70)

entries = LedgerEntry.objects.filter(entity_id=7).order_by('entry_date', 'id')
print(f"\nTotal Entries: {entries.count()}\n")

if entries.exists():
    for entry in entries:
        account_type = entry.account.account_type
        print(f"{entry.entry_date} | {entry.reference_number}")
        print(f"  Account: {entry.account.account_number} - {entry.account.name} ({account_type})")
        print(f"  {entry.entry_type}: {entry.amount:,.2f}")
        
        # Validate each transaction
        if 'CASH-RECEIPT' in entry.reference_number:
            if entry.account.account_number == '100001' and entry.entry_type == 'DEBIT':
                print(f"  ✅ CORRECT: Cash Receipt debits Cash account")
            elif entry.account.account_type == 'EQUITY' and entry.entry_type == 'CREDIT':
                print(f"  ✅ CORRECT: Cash Receipt credits Capital account")
            else:
                print(f"  ❌ WRONG!")
                
        elif 'CASH-PAYMENT' in entry.reference_number:
            if entry.account.account_number == '100001' and entry.entry_type == 'CREDIT':
                print(f"  ✅ CORRECT: Cash Payment credits Cash account")
            elif entry.account.account_type == 'EQUITY' and entry.entry_type == 'DEBIT':
                print(f"  ✅ CORRECT: Cash Payment debits Capital account")
            else:
                print(f"  ❌ WRONG!")
                
        elif 'BANK-RECEIPT' in entry.reference_number:
            if entry.account.account_type == 'ASSET' and entry.account.account_number != '100001' and entry.entry_type == 'DEBIT':
                print(f"  ✅ CORRECT: Bank Receipt debits Bank account (not Cash)")
            elif entry.account.account_type == 'EQUITY' and entry.entry_type == 'CREDIT':
                print(f"  ✅ CORRECT: Bank Receipt credits Capital account")
            else:
                print(f"  ❌ WRONG!")
                
        elif 'BANK-PAYMENT' in entry.reference_number:
            if entry.account.account_type == 'ASSET' and entry.account.account_number != '100001' and entry.entry_type == 'CREDIT':
                print(f"  ✅ CORRECT: Bank Payment credits Bank account (not Cash)")
            elif entry.account.account_type == 'EQUITY' and entry.entry_type == 'DEBIT':
                print(f"  ✅ CORRECT: Bank Payment debits Capital account")
            else:
                print(f"  ❌ WRONG!")
        print()

# Calculate account balances
print("="*70)
print("ACCOUNT BALANCES")
print("="*70)

# Cash account
cash_result = LedgerEntry.objects.filter(
    entity_id=7,
    account__account_number='100001'
).aggregate(
    debits=Sum('amount', filter=Q(entry_type='DEBIT')),
    credits=Sum('amount', filter=Q(entry_type='CREDIT'))
)

cash_debits = cash_result['debits'] or Decimal('0')
cash_credits = cash_result['credits'] or Decimal('0')
cash_balance = cash_debits - cash_credits

print(f"\nCash Account (100001):")
print(f"  Debits:  {cash_debits:>15,.2f}")
print(f"  Credits: {cash_credits:>15,.2f}")
print(f"  Balance: {cash_balance:>15,.2f}")

if cash_balance >= 0:
    print(f"  ✅ Normal DEBIT balance (positive)")
else:
    print(f"  ❌ Abnormal CREDIT balance (negative)")

# Capital account
capital_result = LedgerEntry.objects.filter(
    entity_id=7,
    account__account_number='3000-11'
).aggregate(
    debits=Sum('amount', filter=Q(entry_type='DEBIT')),
    credits=Sum('amount', filter=Q(entry_type='CREDIT'))
)

capital_debits = capital_result['debits'] or Decimal('0')
capital_credits = capital_result['credits'] or Decimal('0')
capital_balance = capital_debits - capital_credits

print(f"\nCapital Account (3000-11):")
print(f"  Debits:  {capital_debits:>15,.2f}")
print(f"  Credits: {capital_credits:>15,.2f}")
print(f"  Balance: {capital_balance:>15,.2f}")

if capital_balance < 0:
    print(f"  ✅ Normal CREDIT balance for EQUITY (negative)")
else:
    print(f"  ❌ Abnormal DEBIT balance")

# Check for bank accounts
bank_entries = LedgerEntry.objects.filter(
    entity_id=7,
    account__account_type='ASSET'
).exclude(account__account_number='100001')

if bank_entries.exists():
    bank_accounts = {}
    for entry in bank_entries:
        acc_num = entry.account.account_number
        if acc_num not in bank_accounts:
            bank_accounts[acc_num] = {
                'name': entry.account.name,
                'debits': Decimal('0'),
                'credits': Decimal('0')
            }
        if entry.entry_type == 'DEBIT':
            bank_accounts[acc_num]['debits'] += entry.amount
        else:
            bank_accounts[acc_num]['credits'] += entry.amount
    
    for acc_num, data in bank_accounts.items():
        balance = data['debits'] - data['credits']
        print(f"\nBank Account ({acc_num} - {data['name']}):")
        print(f"  Debits:  {data['debits']:>15,.2f}")
        print(f"  Credits: {data['credits']:>15,.2f}")
        print(f"  Balance: {balance:>15,.2f}")
        if balance >= 0:
            print(f"  ✅ Normal DEBIT balance")
        else:
            print(f"  ❌ Abnormal CREDIT balance")

# Check Balance Sheet
print("\n" + "="*70)
print("BALANCE SHEET CHECK")
print("="*70)

# Calculate totals by type
asset_total = Decimal('0')
liability_total = Decimal('0')
equity_total = Decimal('0')

all_entries = LedgerEntry.objects.filter(entity_id=7)
accounts_data = {}

for entry in all_entries:
    acc_id = entry.account.id
    if acc_id not in accounts_data:
        accounts_data[acc_id] = {
            'account': entry.account,
            'debits': Decimal('0'),
            'credits': Decimal('0')
        }
    if entry.entry_type == 'DEBIT':
        accounts_data[acc_id]['debits'] += entry.amount
    else:
        accounts_data[acc_id]['credits'] += entry.amount

for data in accounts_data.values():
    balance = data['debits'] - data['credits']
    acc_type = data['account'].account_type
    
    if acc_type == 'ASSET' and balance > 0:
        asset_total += balance
    elif acc_type == 'LIABILITY' and balance < 0:
        liability_total += abs(balance)
    elif acc_type == 'EQUITY' and balance < 0:
        equity_total += abs(balance)

print(f"\nTotal Assets:      {asset_total:>15,.2f}")
print(f"Total Liabilities: {liability_total:>15,.2f}")
print(f"Total Equity:      {equity_total:>15,.2f}")
print(f"\nLiab + Equity:     {(liability_total + equity_total):>15,.2f}")

is_balanced = abs(asset_total - (liability_total + equity_total)) < Decimal('0.01')
print(f"\nBalanced: {'✅ YES' if is_balanced else '❌ NO'}")

print("\n" + "="*70)
print("EXPECTED VALUES:")
print("="*70)
print("Cash: 100,000 - 500 = 99,500")
print("Bank: 1,000 - 200 = 800")
print("Total Assets: 99,500 + 800 = 100,300")
print("Capital: 100,000 + 1,000 - 500 - 200 = 100,300")
print("Total Equity: 100,300")
print("="*70)
