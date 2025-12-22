#!/usr/bin/env python3
"""
Investigate cash position calculation
"""
import os
import django
import sys
from decimal import Decimal
from datetime import date, timedelta

# Add the project directory to the Python path
sys.path.append('/var/www/tradifyerp')

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')

# Setup Django
django.setup()

# Import models
from cash_management.models import CashPosition
from accounting.models import LedgerEntry, Account, Entity

print("INVESTIGATING CASH POSITION CALCULATION")
print("======================================")

# Get Testing entity
entity = Entity.objects.get(name="Testing")
print(f"Entity: {entity.name}")

# Check cash account
cash_account = Account.objects.get(entity=entity, account_number='100001')
print(f"\nCash Account: {cash_account.account_number} - {cash_account.name}")

# Get ledger entries for cash account
cash_entries = LedgerEntry.objects.filter(account=cash_account).order_by('-entry_date', '-id')
print(f"\nLedger Entries for Cash Account: {cash_entries.count()}")

total_debits = Decimal('0')
total_credits = Decimal('0')

for entry in cash_entries:
    print(f"\n  ID {entry.id}:")
    print(f"    Date: {entry.entry_date}")
    print(f"    Type: {entry.entry_type}")
    print(f"    Amount: {entry.amount}")
    print(f"    Description: {entry.description}")
    
    if entry.entry_type == 'DEBIT':
        total_debits += entry.amount
    else:
        total_credits += entry.amount

print(f"\nCash Account Calculation:")
print(f"  Total Debits: {total_debits}")
print(f"  Total Credits: {total_credits}")
print(f"  Net Balance (Debits - Credits): {total_debits - total_credits}")

# Check CashPosition records
print(f"\n2. CASH POSITION RECORDS:")
today = date.today()
print(f"Looking for CashPosition records for today: {today}")

cash_positions = CashPosition.objects.filter(position_date=today)
print(f"CashPosition records for {today}: {cash_positions.count()}")

for pos in cash_positions:
    print(f"\n  ID: {pos.id}")
    print(f"    Bank Account: {pos.bank_account}")
    print(f"    Position Date: {pos.position_date}")
    print(f"    Opening Balance: {pos.opening_balance}")
    print(f"    Closing Balance: {pos.closing_balance}")
    print(f"    Entity: {pos.entity if hasattr(pos, 'entity') else 'N/A'}")

# Check all CashPosition records (not just today)
print(f"\n3. ALL CASH POSITION RECORDS:")
all_positions = CashPosition.objects.all().order_by('-position_date')
print(f"Total CashPosition records: {all_positions.count()}")

for pos in all_positions[:10]:  # Show last 10
    print(f"\n  {pos.position_date}: {pos.bank_account} - {pos.closing_balance}")

# Check the dashboard calculation
print(f"\n4. DASHBOARD CALCULATION (today={today}):")
latest_positions = CashPosition.objects.filter(position_date=today)
print(f"Positions found: {latest_positions.count()}")

from django.db.models import Sum
total_cash = latest_positions.aggregate(total=Sum('closing_balance'))['total'] or Decimal('0')
print(f"Total Cash (sum of closing_balance): {total_cash}")

print("\nDebug complete.")