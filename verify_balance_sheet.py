from accounting.models import LedgerEntry, Account, Entity, BalanceSheet
from django.db.models import Sum, Q
from decimal import Decimal

print("\n" + "="*70)
print("BALANCE SHEET VERIFICATION FOR TEST ENTITY")
print("="*70)

# Get Test entity
test_entity = Entity.objects.get(code='Test')
print(f"\nEntity: {test_entity.name} (ID: {test_entity.id})")

# Check all ledger entries
entries = LedgerEntry.objects.filter(entity=test_entity)
print(f"\nTotal Ledger Entries: {entries.count()}")

if entries.exists():
    print("\nLedger Entries:")
    for entry in entries.order_by('entry_date', 'id'):
        print(f"  {entry.entry_date} | {entry.account.account_number} - {entry.account.name}")
        print(f"    {entry.entry_type}: {entry.amount:,.2f} | Ref: {entry.reference_number}")
        print(f"    Status: {entry.workflow_status}")
    
    # Calculate balances by account type
    print("\n" + "="*70)
    print("ACCOUNT BALANCES BY TYPE")
    print("="*70)
    
    accounts_data = {}
    for entry in entries:
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
    
    # Group by account type
    by_type = {
        'ASSET': {'accounts': [], 'total': Decimal('0')},
        'LIABILITY': {'accounts': [], 'total': Decimal('0')},
        'EQUITY': {'accounts': [], 'total': Decimal('0')},
        'INCOME': {'accounts': [], 'total': Decimal('0')},
        'EXPENSE': {'accounts': [], 'total': Decimal('0')}
    }
    
    for acc_data in accounts_data.values():
        account = acc_data['account']
        balance = acc_data['debits'] - acc_data['credits']
        
        account_info = {
            'number': account.account_number,
            'name': account.name,
            'debits': acc_data['debits'],
            'credits': acc_data['credits'],
            'balance': balance
        }
        
        if account.account_type in by_type:
            by_type[account.account_type]['accounts'].append(account_info)
    
    # Print details
    for acc_type, data in by_type.items():
        if data['accounts']:
            print(f"\n{acc_type} ACCOUNTS:")
            for acc in data['accounts']:
                print(f"  {acc['number']} - {acc['name']}")
                print(f"    Debits:  {acc['debits']:>12,.2f}")
                print(f"    Credits: {acc['credits']:>12,.2f}")
                print(f"    Balance: {acc['balance']:>12,.2f}")
                
                # Calculate contribution to balance sheet
                if acc_type == 'ASSET':
                    if acc['balance'] > 0:
                        data['total'] += acc['balance']
                        print(f"    → Asset: {acc['balance']:>12,.2f}")
                elif acc_type == 'LIABILITY':
                    if acc['balance'] < 0:
                        data['total'] += abs(acc['balance'])
                        print(f"    → Liability: {abs(acc['balance']):>12,.2f}")
                elif acc_type == 'EQUITY':
                    if acc['balance'] < 0:
                        data['total'] += abs(acc['balance'])
                        print(f"    → Equity: {abs(acc['balance']):>12,.2f}")
    
    print("\n" + "="*70)
    print("BALANCE SHEET SUMMARY")
    print("="*70)
    print(f"Total Assets:      {by_type['ASSET']['total']:>12,.2f}")
    print(f"Total Liabilities: {by_type['LIABILITY']['total']:>12,.2f}")
    print(f"Total Equity:      {by_type['EQUITY']['total']:>12,.2f}")
    print(f"Liab + Equity:     {(by_type['LIABILITY']['total'] + by_type['EQUITY']['total']):>12,.2f}")
    
    is_balanced = abs(by_type['ASSET']['total'] - (by_type['LIABILITY']['total'] + by_type['EQUITY']['total'])) < Decimal('0.01')
    print(f"\nBalanced: {is_balanced}")
    
else:
    print("\nNo ledger entries found for Test entity.")
    print("Balance Sheet should show all zeros - CORRECT!")

# Check existing balance sheets
print("\n" + "="*70)
print("EXISTING BALANCE SHEETS IN DATABASE")
print("="*70)

balance_sheets = BalanceSheet.objects.filter(entity=test_entity).order_by('-as_of_date')
if balance_sheets.exists():
    for bs in balance_sheets:
        print(f"\nDate: {bs.as_of_date}")
        print(f"  Assets:      {bs.total_assets:,.2f}")
        print(f"  Liabilities: {bs.total_liabilities:,.2f}")
        print(f"  Equity:      {bs.total_equity:,.2f}")
        print(f"  Created:     {bs.created_at}")
else:
    print("\nNo balance sheets found in database.")

print("\n" + "="*70)
