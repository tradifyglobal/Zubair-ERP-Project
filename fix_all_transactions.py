from accounting.models import LedgerEntry, CashReceiptLine, CashPaymentLine, BankReceiptLine, BankPaymentLine

print("\n" + "="*70)
print("STEP 1: DELETE ALL INCORRECT LEDGER ENTRIES")
print("="*70)

# Delete all ledger entries for Test entity
entries = LedgerEntry.objects.filter(entity_id=7)
count = entries.count()
print(f"\nFound {count} ledger entries for Test entity")
print("\nDeleting:")
for entry in entries:
    print(f"  {entry.reference_number} | {entry.account} | {entry.entry_type} {entry.amount:,.2f}")

entries.delete()
print(f"\n✅ Deleted {count} ledger entries")

print("\n" + "="*70)
print("STEP 2: RESET TRANSACTIONS TO APPROVED STATUS")
print("="*70)

# Reset cash receipt 13
try:
    receipt = CashReceiptLine.objects.get(id=13)
    print(f"\nCash Receipt 13:")
    print(f"  Current: {receipt.workflow_status} / {receipt.status}")
    receipt.workflow_status = 'APPROVED'
    receipt.status = 'PENDING'
    receipt.save()
    print(f"  Updated: {receipt.workflow_status} / {receipt.status}")
    print(f"  ✅ Ready for re-authorization")
except CashReceiptLine.DoesNotExist:
    print("\n  Cash Receipt 13 not found")

# Reset cash payment 15  
try:
    payment = CashPaymentLine.objects.get(id=15)
    print(f"\nCash Payment 15:")
    print(f"  Current: {payment.workflow_status} / {payment.status}")
    payment.workflow_status = 'APPROVED'
    payment.status = 'PENDING'
    payment.save()
    print(f"  Updated: {payment.workflow_status} / {payment.status}")
    print(f"  ✅ Ready for re-authorization")
except CashPaymentLine.DoesNotExist:
    print("\n  Cash Payment 15 not found")

# Reset bank receipt 7
try:
    bank_receipt = BankReceiptLine.objects.get(id=7)
    print(f"\nBank Receipt 7:")
    print(f"  Current: {bank_receipt.workflow_status} / {bank_receipt.status}")
    bank_receipt.workflow_status = 'APPROVED'
    bank_receipt.status = 'PENDING'
    bank_receipt.save()
    print(f"  Updated: {bank_receipt.workflow_status} / {bank_receipt.status}")
    print(f"  ✅ Ready for re-authorization")
except BankReceiptLine.DoesNotExist:
    print("\n  Bank Receipt 7 not found")

# Reset bank payment 4
try:
    bank_payment = BankPaymentLine.objects.get(id=4)
    print(f"\nBank Payment 4:")
    print(f"  Current: {bank_payment.workflow_status} / {bank_payment.status}")
    bank_payment.workflow_status = 'APPROVED'
    bank_payment.status = 'PENDING'
    bank_payment.save()
    print(f"  Updated: {bank_payment.workflow_status} / {bank_payment.status}")
    print(f"  ✅ Ready for re-authorization")
except BankPaymentLine.DoesNotExist:
    print("\n  Bank Payment 4 not found")

print("\n" + "="*70)
print("CLEANUP COMPLETE!")
print("="*70)
print("\nNext steps:")
print("1. Go to Cash Receipts page and authorize receipt 13")
print("2. Go to Cash Payments page and authorize payment 15") 
print("3. Go to Bank Receipts page and authorize receipt 7")
print("4. Go to Bank Payments page and authorize payment 4")
print("\nThe CORRECT ledger entries will be created with:")
print("  Cash Receipt:  DEBIT Cash, CREDIT Capital")
print("  Cash Payment:  DEBIT Capital, CREDIT Cash")
print("  Bank Receipt:  DEBIT Bank, CREDIT Capital")
print("  Bank Payment:  DEBIT Capital, CREDIT Bank")
print("="*70)
