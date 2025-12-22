from accounting.models import CashReceiptLine, CashPaymentLine, BankReceiptLine, BankPaymentLine

print("\n" + "="*70)
print("CHECKING TRANSACTION AMOUNTS")
print("="*70)

# Check cash receipt
receipts = CashReceiptLine.objects.filter(id=13)
if receipts.exists():
    receipt = receipts.first()
    print(f"\nCASH-RECEIPT-13:")
    print(f"  Account: {receipt.account}")
    print(f"  Debit Amount: {receipt.debit_amount}")
    print(f"  Credit Amount: {receipt.credit_amount}")
    print(f"  Amount field: {receipt.amount}")
    print(f"  Status: {receipt.workflow_status}")
    print(f"  \nExpected:")
    print(f"    DEBIT Cash: {receipt.amount}")
    print(f"    CREDIT Capital: {receipt.amount}")

# Check cash payment  
payments = CashPaymentLine.objects.filter(id=15)
if payments.exists():
    payment = payments.first()
    print(f"\nCASH-PAYMENT-15:")
    print(f"  Account: {payment.account}")
    print(f"  Debit Amount: {payment.debit_amount}")
    print(f"  Credit Amount: {payment.credit_amount}")
    print(f"  Amount field: {payment.amount}")
    print(f"  Status: {payment.workflow_status}")

# Check bank receipt
bank_receipts = BankReceiptLine.objects.filter(id=7)
if bank_receipts.exists():
    br = bank_receipts.first()
    print(f"\nBANK-RECEIPT-7:")
    print(f"  Account: {br.account}")
    print(f"  Debit Amount: {br.debit_amount if hasattr(br, 'debit_amount') else 'N/A'}")
    print(f"  Credit Amount: {br.credit_amount if hasattr(br, 'credit_amount') else 'N/A'}")
    print(f"  Amount field: {br.amount}")
    print(f"  Bank Account: {br.bank_account if hasattr(br, 'bank_account') else 'N/A'}")
    print(f"  Status: {br.workflow_status}")

# Check bank payment
bank_payments = BankPaymentLine.objects.filter(id=4)
if bank_payments.exists():
    bp = bank_payments.first()
    print(f"\nBANK-PAYMENT-4:")
    print(f"  Account: {bp.account}")
    print(f"  Debit Amount: {bp.debit_amount if hasattr(bp, 'debit_amount') else 'N/A'}")
    print(f"  Credit Amount: {bp.credit_amount if hasattr(bp, 'credit_amount') else 'N/A'}")
    print(f"  Amount field: {bp.amount}")
    print(f"  Bank Account: {bp.bank_account if hasattr(bp, 'bank_account') else 'N/A'}")
    print(f"  Status: {bp.workflow_status}")
