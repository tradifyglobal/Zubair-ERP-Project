from accounting.models import CashReceiptLine, CashPaymentLine, Entity

entity = Entity.objects.first()

print("\n" + "="*80)
print("CASH RECEIPTS STATUS")
print("="*80)

receipts = CashReceiptLine.objects.filter(entity=entity).order_by('-date')
if receipts.exists():
    print(f"\nTotal cash receipts: {receipts.count()}\n")
    print(f"{'ID':<6} {'Date':<12} {'Account':<40} {'Amount':<15} {'Status':<15}")
    print("-"*100)
    for r in receipts:
        acc_display = f"{r.account.account_number} - {r.account.name}"
        print(f"{r.id:<6} {str(r.date):<12} {acc_display[:38]:<40} {r.debit_amount:>14,.2f} {r.workflow_status:<15}")
else:
    print("\nNo cash receipts found")

print("\n" + "="*80)
print("CASH PAYMENTS STATUS")
print("="*80)

payments = CashPaymentLine.objects.filter(entity=entity).order_by('-date')
if payments.exists():
    print(f"\nTotal cash payments: {payments.count()}\n")
    print(f"{'ID':<6} {'Date':<12} {'Account':<40} {'Amount':<15} {'Status':<15}")
    print("-"*100)
    for p in payments:
        acc_display = f"{p.account.account_number} - {p.account.name}"
        print(f"{p.id:<6} {str(p.date):<12} {acc_display[:38]:<40} {p.debit_amount:>14,.2f} {p.workflow_status:<15}")
else:
    print("\nNo cash payments found")

print("\n" + "="*80)
print("ACTION REQUIRED")
print("="*80)
print("""
To populate GL Dashboard and Trial Balance:

1. Go to Cash Receipts page: https://tradifyglobal.com/accounting/cash-receipts/
2. If receipts exist with DRAFT or APPROVED status:
   - Click "Approve" button (if DRAFT)
   - Then click "Authorize and Post" button
   
3. Or create a new cash receipt:
   - Click "+ New Cash Receipt"
   - Fill in details
   - Approve and Authorize

Only AUTHORIZED transactions create ledger entries that show in GL Dashboard and Trial Balance!
""")
