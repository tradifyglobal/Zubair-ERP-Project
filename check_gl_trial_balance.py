from accounting.models import LedgerEntry, Account, Entity
from decimal import Decimal

entity = Entity.objects.first()

print("\n" + "="*80)
print("GL DASHBOARD CHECK - AUTHORIZED LEDGER ENTRIES")
print("="*80)

# Check what GL Dashboard would show (excludes DRAFT/REJECTED)
gl_entries = LedgerEntry.objects.filter(
    entity=entity
).exclude(
    workflow_status__in=['DRAFT', 'REJECTED']
).order_by('-entry_date', '-created_at')[:20]

if gl_entries.exists():
    print(f"\nFound {gl_entries.count()} authorized entries:\n")
    print(f"{'ID':<6} {'Date':<12} {'Account':<50} {'DR/CR':<6} {'Amount':<15} {'Status':<12}")
    print("-"*110)
    for e in gl_entries:
        acc_display = f"{e.account.account_number} - {e.account.name}"
        print(f"{e.id:<6} {str(e.entry_date):<12} {acc_display[:48]:<50} {e.entry_type:<6} {e.amount:>14,.2f} {e.workflow_status:<12}")
else:
    print("\nNo authorized ledger entries found!")
    print("GL Dashboard will be empty.")

print("\n" + "="*80)
print("TRIAL BALANCE CALCULATION")
print("="*80)

# Calculate trial balance like the view does
from accounting.trial_balance import calculate_trial_balance
from datetime import date

tb_data = calculate_trial_balance(entity, date.today())

if tb_data and tb_data['account_balances']:
    print(f"\nTrial Balance as of {date.today()}")
    print(f"Total Debits: {tb_data['total_debits']:,.2f}")
    print(f"Total Credits: {tb_data['total_credits']:,.2f}")
    print(f"Balanced: {tb_data['is_balanced']}")
    print(f"\nAccount Balances ({len(tb_data['account_balances'])} accounts):\n")
    print(f"{'Account':<50} {'Debit':<15} {'Credit':<15}")
    print("-"*80)
    for bal in tb_data['account_balances']:
        acc_name = f"{bal['account_number']} - {bal['account_name']}"
        print(f"{acc_name[:48]:<50} {bal['debit_balance']:>14,.2f} {bal['credit_balance']:>14,.2f}")
else:
    print("\nNo trial balance data!")
    print("Trial Balance page will show: 'No GL entries found'")

print("\n" + "="*80)
print("ALL LEDGER ENTRIES (including DRAFT)")
print("="*80)

all_entries = LedgerEntry.objects.filter(entity=entity).order_by('-entry_date')[:10]
print(f"\nTotal entries in database: {LedgerEntry.objects.filter(entity=entity).count()}")
print(f"\nRecent 10 entries (all statuses):\n")
print(f"{'ID':<6} {'Date':<12} {'Account':<40} {'Type':<6} {'Amount':<15} {'Status':<12}")
print("-"*100)
for e in all_entries:
    acc_display = f"{e.account.account_number} - {e.account.name}"
    print(f"{e.id:<6} {str(e.entry_date):<12} {acc_display[:38]:<40} {e.entry_type:<6} {e.amount:>14,.2f} {e.workflow_status:<12}")
