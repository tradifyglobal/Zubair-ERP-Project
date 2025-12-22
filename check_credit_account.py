from accounting.models import CashReceiptLine

receipts = CashReceiptLine.objects.all().order_by('-date')[:5]

print("\n" + "="*80)
print("CASH RECEIPTS - CREDIT ACCOUNT CHECK")
print("="*80)

for r in receipts:
    print(f"\nID: {r.id}")
    print(f"Date: {r.date}")
    print(f"Description: {r.description}")
    print(f"Debit Account: {r.account.account_number} - {r.account.name}")
    print(f"credit_account value: {r.credit_account}")
    print(f"credit_account is None: {r.credit_account is None}")
    print(f"credit_account type: {type(r.credit_account)}")
    if r.credit_account:
        print(f"Credit Account: {r.credit_account.account_number} - {r.credit_account.name}")
    else:
        print("Credit Account: NONE - Should show 100001 Cash Account")
    print("-"*80)
