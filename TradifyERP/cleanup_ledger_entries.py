import os
import django
import sys

# Add the project directory to the Python path
sys.path.append('/var/www/tradifyerp')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')

django.setup()

from accounting.models import LedgerEntry

# Find and delete the specified ledger entries
reference_numbers = ['EXP-6-7', 'EXP-5-6', 'EXP-5-5']
account_id = 59224

print(f"Looking for ledger entries with references: {reference_numbers}")
print(f"For account ID: {account_id}")
print("-" * 80)

entries = LedgerEntry.objects.filter(
    reference_number__in=reference_numbers,
    account_id=account_id
)

print(f"\nFound {entries.count()} entries to delete:")
for entry in entries:
    print(f"ID: {entry.id}, Date: {entry.date}, Ref: {entry.reference_number}, "
          f"Description: {entry.description}, Debit: {entry.debit}, Credit: {entry.credit}")

if entries.count() > 0:
    confirm = input(f"\nDo you want to delete these {entries.count()} entries? (yes/no): ")
    if confirm.lower() == 'yes':
        count = entries.count()
        entries.delete()
        print(f"\n✓ Successfully deleted {count} ledger entries!")
    else:
        print("\n✗ Deletion cancelled.")
else:
    print("\nNo entries found to delete.")
