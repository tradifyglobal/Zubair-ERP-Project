from accounting.models import CashPaymentLine, BankReceiptLine, BankPaymentLine

print("\nCASH-PAYMENT-15:")
payment = CashPaymentLine.objects.get(id=15)
print(f"  payment.account: {payment.account}")
print(f"  payment.credit_account: {payment.credit_account}")
print(f"  \nCode does:")
print(f"    DEBIT payment.account ({payment.account})")
print(f"    CREDIT cash_account (100001)")
print(f"  \nShould be:")
print(f"    DEBIT Capital account")
print(f"    CREDIT Cash (100001)")

print("\n\nBANK-RECEIPT-7:")
br = BankReceiptLine.objects.get(id=7)
print(f"  bank_receipt.account: {br.account}")
print(f"  bank_receipt.bank_account: {br.bank_account if hasattr(br, 'bank_account') else 'N/A'}")
print(f"  \nShould use Bank Account, NOT Cash!")

print("\n\nBANK-PAYMENT-4:")
bp = BankPaymentLine.objects.get(id=4)
print(f"  bank_payment.account: {bp.account}")
print(f"  bank_payment.bank_account: {bp.bank_account if hasattr(bp, 'bank_account') else 'N/A'}")
print(f"  \nShould use Bank Account, NOT Cash!")
