from accounting.models import LedgerEntry, CashPaymentLine, BankReceiptLine, BankPaymentLine

print("\n" + "="*70)
print("FIXING INCORRECT LEDGER ENTRIES")
print("="*70)

# Delete the 6 wrong entries (keeping cash receipt which is correct)
wrong_entries = LedgerEntry.objects.filter(
    entity_id=7,
    reference_number__in=['CASH-PAYMENT-15', 'BANK-RECEIPT-7', 'BANK-PAYMENT-4']
)

print(f"\nDeleting {wrong_entries.count()} incorrect entries:")
for entry in wrong_entries:
    print(f"  {entry.reference_number} | {entry.account} | {entry.entry_type} {entry.amount:,.2f}")

wrong_entries.delete()

# Reset the transactions
print("\n" + "="*70)
print("RESETTING TRANSACTIONS")
print("="*70)

try:
    payment = CashPaymentLine.objects.get(id=15)
    print(f"\nCash Payment 15: {payment.workflow_status} →  APPROVED")
    payment.workflow_status = 'APPROVED'
    payment.status = 'PENDING'
    payment.save()
except:
    print("Cash Payment 15 not found")

try:
    br = BankReceiptLine.objects.get(id=7)
    print(f"Bank Receipt 7: {br.workflow_status} → APPROVED")
    br.workflow_status = 'APPROVED'
    br.status = 'PENDING'
    br.save()
except:
    print("Bank Receipt 7 not found")

try:
    bp = BankPaymentLine.objects.get(id=4)
    print(f"Bank Payment 4: {bp.workflow_status} → APPROVED")
    bp.workflow_status = 'APPROVED'
    bp.status = 'PENDING'
    bp.save()
except:
    print("Bank Payment 4 not found")

print("\n" + "="*70)
print("INSTRUCTIONS")
print("="*70)
print("\n⚠️  THE PROBLEM: Wrong accounts selected when creating transactions!")
print("\nFor CASH PAYMENT:")
print("  Current setup:")
print("    account = Cash (100001) ← WRONG!")
print("    credit_account = Capital (3000-11)")
print("  Should be:")
print("    account = Capital (3000-11)")
print("    credit_account = Cash (100001) or leave blank")
print("\nFor BANK RECEIPT/PAYMENT:")
print("  Need to select an actual BANK account")
print("  (e.g., 1000 Bank Account)")
print("  Currently using Cash (100001) which is wrong!")
print("\n" + "="*70)
print("NEXT STEPS:")
print("="*70)
print("1. DELETE these transactions and create new ones with correct accounts")
print("   OR")
print("2. Update the account fields in the database directly")
print("\nDo you want me to:")
print("a) Update the accounts in the database? (quick fix)")
print("b) Provide instructions to recreate transactions? (clean approach)")
print("="*70)
