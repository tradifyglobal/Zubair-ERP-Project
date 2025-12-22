from accounting.models import LedgerEntry
from django.db.models import Sum, Q

result = LedgerEntry.objects.filter(
    account_id='100001',
    entity_id=7
).aggregate(
    debits=Sum('amount', filter=Q(entry_type='DEBIT')),
    credits=Sum('amount', filter=Q(entry_type='CREDIT'))
)

debits = result['debits'] or 0
credits = result['credits'] or 0
balance = debits - credits

print(f"\nCash Account (100001) - Test Entity")
print("=" * 50)
print(f"Total Debits:  {debits:>15,.2f}")
print(f"Total Credits: {credits:>15,.2f}")
print("-" * 50)
print(f"Cash Balance:  {balance:>15,.2f}")
print("=" * 50)
