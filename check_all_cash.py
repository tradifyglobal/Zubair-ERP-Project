from accounting.models import LedgerEntry, CashReceiptLine, CashPaymentLine, Entity
from django.db.models import Sum, Q, Count

print("\n" + "="*70)
print("CASH TRANSACTIONS BY ENTITY")
print("="*70)

# Check ledger entries for cash account by entity
entities = Entity.objects.all()
for entity in entities:
    result = LedgerEntry.objects.filter(
        account_id='100001',
        entity_id=entity.id
    ).aggregate(
        count=Count('id'),
        debits=Sum('amount', filter=Q(entry_type='DEBIT')),
        credits=Sum('amount', filter=Q(entry_type='CREDIT'))
    )
    
    if result['count'] > 0:
        debits = result['debits'] or 0
        credits = result['credits'] or 0
        balance = debits - credits
        print(f"\n{entity.name} (ID: {entity.id}):")
        print(f"  Ledger Entries: {result['count']}")
        print(f"  Debits:  {debits:>12,.2f}")
        print(f"  Credits: {credits:>12,.2f}")
        print(f"  Balance: {balance:>12,.2f}")

print("\n" + "="*70)
print("PENDING CASH RECEIPTS (APPROVED but not AUTHORIZED)")
print("="*70)

pending_receipts = CashReceiptLine.objects.filter(
    workflow_status='APPROVED',
    status='PENDING'
).select_related('entity', 'capital_account')

if pending_receipts.exists():
    for receipt in pending_receipts:
        print(f"\nReceipt ID: {receipt.id}")
        print(f"  Entity: {receipt.entity.name}")
        print(f"  Amount: {receipt.amount:,.2f}")
        print(f"  Capital Account: {receipt.capital_account}")
        print(f"  Date: {receipt.receipt_date}")
        print(f"  Status: {receipt.workflow_status} / {receipt.status}")
else:
    print("\nNo pending cash receipts found.")

print("\n" + "="*70)
print("PENDING CASH PAYMENTS (APPROVED but not AUTHORIZED)")
print("="*70)

pending_payments = CashPaymentLine.objects.filter(
    workflow_status='APPROVED',
    status='PENDING'
).select_related('entity', 'capital_account')

if pending_payments.exists():
    for payment in pending_payments:
        print(f"\nPayment ID: {payment.id}")
        print(f"  Entity: {payment.entity.name}")
        print(f"  Amount: {payment.amount:,.2f}")
        print(f"  Capital Account: {payment.capital_account}")
        print(f"  Date: {payment.payment_date}")
        print(f"  Status: {payment.workflow_status} / {payment.status}")
else:
    print("\nNo pending cash payments found.")

print("\n" + "="*70)
