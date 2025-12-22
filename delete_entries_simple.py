from accounting.models import LedgerEntry
from django.db import transaction

refs = ['CASH-RECEIPT-16', 'CASH-RECEIPT-17', 'CASH-PAYMENT-25']
entries = LedgerEntry.objects.filter(reference_number__in=refs)

print(f"Found {entries.count()} entries to delete:")
for e in entries:
    print(f"  ID {e.id}: {e.reference_number} - {e.entry_type} - {e.account.account_number} - ₹{e.amount}")

with transaction.atomic():
    count, details = entries.delete()
    print(f"\n✅ Deleted {count} total records:")
    for model, num in details.items():
        print(f"   {model}: {num}")
