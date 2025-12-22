from accounting.models import LedgerEntry, Account

print("\n" + "="*70)
print("INVESTIGATING CASH ACCOUNT ID")
print("="*70)

# Find all accounts with "100001" or "Cash" in them
cash_accounts = Account.objects.filter(account_number__contains='100001')
print(f"\nAccounts with '100001':")
for acc in cash_accounts:
    print(f"  ID: {acc.id} | Number: {acc.account_number} | Name: {acc.name}")

cash_accounts2 = Account.objects.filter(name__icontains='cash')
print(f"\nAccounts with 'cash' in name:")
for acc in cash_accounts2:
    print(f"  ID: {acc.id} | Number: {acc.account_number} | Name: {acc.name} | Type: {acc.account_type}")

# Check all ledger entries for Test entity
print("\n" + "="*70)
print("ALL LEDGER ENTRIES FOR TEST ENTITY")
print("="*70)

entries = LedgerEntry.objects.filter(entity_id=7).order_by('entry_date', 'id')
print(f"\nTotal: {entries.count()}\n")

for entry in entries:
    print(f"Account ID: {entry.account.id} | Account: {entry.account.account_number} - {entry.account.name}")
    print(f"  Date: {entry.entry_date} | Type: {entry.entry_type} | Amount: {entry.amount:,.2f}")
    print(f"  Ref: {entry.reference_number} | Status: {entry.workflow_status}")
    print()
