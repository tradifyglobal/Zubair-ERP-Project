from accounting.models import CashReceiptLine

receipt = CashReceiptLine.objects.get(id=13)
print(f"\nCASH-RECEIPT-13:")
print(f"  receipt.account: {receipt.account} (ID: {receipt.account.id})")
print(f"  receipt.account.account_number: {receipt.account.account_number}")
print(f"  receipt.credit_account: {receipt.credit_account}")
print(f"  \nThe code does:")
print(f"    if receipt.credit_account: cash_account = receipt.credit_account")
print(f"    else: cash_account = Account 100001")
print(f"  \nSo cash_account will be: {receipt.credit_account if receipt.credit_account else 'Account 100001'}")
print(f"  \nThen:")
print(f"    DEBIT to cash_account")
print(f"    CREDIT to receipt.account ({receipt.account})")
