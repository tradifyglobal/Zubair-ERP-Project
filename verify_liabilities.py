from accounting.models import LedgerEntry, Account
from django.db.models import Sum, Q
from decimal import Decimal

print("\n" + "="*70)
print("LIABILITY VERIFICATION")
print("="*70)

# Get all ledger entries for Test entity
entries = LedgerEntry.objects.filter(entity_id=7).order_by('entry_date', 'id')

# Calculate balances by account
accounts_data = {}
for entry in entries:
    acc_id = entry.account.id
    if acc_id not in accounts_data:
        accounts_data[acc_id] = {
            'account': entry.account,
            'number': entry.account.account_number,
            'name': entry.account.name,
            'type': entry.account.account_type,
            'debits': Decimal('0'),
            'credits': Decimal('0')
        }
    
    if entry.entry_type == 'DEBIT':
        accounts_data[acc_id]['debits'] += entry.amount
    else:
        accounts_data[acc_id]['credits'] += entry.amount

# Group by account type
by_type = {
    'ASSET': [],
    'LIABILITY': [],
    'EQUITY': []
}

for acc_data in accounts_data.values():
    balance = acc_data['debits'] - acc_data['credits']
    acc_data['balance'] = balance
    
    if acc_data['type'] in by_type:
        by_type[acc_data['type']].append(acc_data)

# Display each type
print("\n" + "="*70)
print("ASSETS")
print("="*70)
asset_total = Decimal('0')
for acc in sorted(by_type['ASSET'], key=lambda x: x['number']):
    print(f"\n{acc['number']} - {acc['name']}")
    print(f"  Debits:  {acc['debits']:>15,.2f}")
    print(f"  Credits: {acc['credits']:>15,.2f}")
    print(f"  Balance: {acc['balance']:>15,.2f}")
    
    if acc['balance'] > 0:
        asset_total += acc['balance']
        print(f"  βî£ Contributes {acc['balance']:,.2f} to Total Assets")

print(f"\nTOTAL ASSETS: {asset_total:,.2f}")

print("\n" + "="*70)
print("LIABILITIES")
print("="*70)
liability_total = Decimal('0')
for acc in sorted(by_type['LIABILITY'], key=lambda x: x['number']):
    print(f"\n{acc['number']} - {acc['name']}")
    print(f"  Debits:  {acc['debits']:>15,.2f}")
    print(f"  Credits: {acc['credits']:>15,.2f}")
    print(f"  Balance: {acc['balance']:>15,.2f}")
    
    # Liabilities have CREDIT balance (negative)
    if acc['balance'] < 0:
        liability_total += abs(acc['balance'])
        print(f"  βî£ Contributes {abs(acc['balance']):,.2f} to Total Liabilities")
        print(f"  βî£ Normal CREDIT balance for LIABILITY")
    else:
        print(f"  Γîî Abnormal DEBIT balance!")

print(f"\nTOTAL LIABILITIES: {liability_total:,.2f}")

print("\n" + "="*70)
print("EQUITY")
print("="*70)
equity_total = Decimal('0')
for acc in sorted(by_type['EQUITY'], key=lambda x: x['number']):
    print(f"\n{acc['number']} - {acc['name']}")
    print(f"  Debits:  {acc['debits']:>15,.2f}")
    print(f"  Credits: {acc['credits']:>15,.2f}")
    print(f"  Balance: {acc['balance']:>15,.2f}")
    
    # Equity has CREDIT balance (negative)
    if acc['balance'] < 0:
        equity_total += abs(acc['balance'])
        print(f"  βî£ Contributes {abs(acc['balance']):,.2f} to Total Equity")

print(f"\nTOTAL EQUITY: {equity_total:,.2f}")

print("\n" + "="*70)
print("BALANCE SHEET SUMMARY")
print("="*70)
print(f"Total Assets:      {asset_total:>15,.2f}")
print(f"Total Liabilities: {liability_total:>15,.2f}")
print(f"Total Equity:      {equity_total:>15,.2f}")
print(f"{'─'*45}")
print(f"Liab + Equity:     {(liability_total + equity_total):>15,.2f}")
print()

difference = abs(asset_total - (liability_total + equity_total))
is_balanced = difference < Decimal('0.01')

if is_balanced:
    print(f"βî£ BALANCED! Assets = Liabilities + Equity")
else:
    print(f"Γîî NOT BALANCED! Difference: {difference:,.2f}")

print("\n" + "="*70)
print("ACCOUNTING EQUATION VERIFICATION")
print("="*70)
print(f"Assets = Liabilities + Equity")
print(f"{asset_total:,.2f} = {liability_total:,.2f} + {equity_total:,.2f}")
print(f"{asset_total:,.2f} = {(liability_total + equity_total):,.2f}")
print(f"{'βî£ CORRECT!' if is_balanced else 'Γîî ERROR!'}")

print("\n" + "="*70)
print("DETAILED BREAKDOWN")
print("="*70)
print("\nAssets:")
print(f"  Cash:  106,500 (100,000 - 500 + 10,000 - 3,000)")
print(f"  Bank:   45,800 (800 + 50,000 - 5,000)")
print(f"  Total: 152,300")
print("\nLiabilities:")
print(f"  Loan Payable:      45,000 (50,000 - 5,000)")
print(f"  Accounts Payable:   7,000 (10,000 - 3,000)")
print(f"  Total:             52,000")
print("\nEquity:")
print(f"  Capital: 100,300")
print("\nTotal Liab + Equity: 152,300")
print("="*70)
