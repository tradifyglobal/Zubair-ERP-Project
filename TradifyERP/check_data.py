#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from accounting.models import Entity, Account, LedgerEntry, Customer, Vendor
from datetime import timedelta
from django.utils import timezone

print("="*60)
print("DATABASE DATA CHECK")
print("="*60)

# Check entities
entities = Entity.objects.all()
print(f"\n✓ Total Entities: {entities.count()}")
for entity in entities[:5]:
    print(f"  - {entity.code}: {entity.name} (Active: {entity.is_active})")

# Get first active entity
entity = Entity.objects.filter(is_active=True).first()
if not entity:
    print("\n✗ ERROR: No active entity found!")
    exit(1)

print(f"\n✓ Using Entity: {entity.code}")

# Check accounts
account_count = entity.accounts.count()
print(f"  - Accounts: {account_count}")
if account_count > 0:
    account_types = entity.accounts.values('account_type').annotate(count=models.Count('id'))
    for at in account_types:
        print(f"      • {at['account_type']}: {at['count']}")

# Check customers and vendors
print(f"  - Customers: {entity.customers.count()}")
print(f"  - Vendors: {entity.vendors.count()}")

# Check ledger entries
ledger_count = entity.ledger_entries.count()
print(f"\n✓ Ledger Entries: {ledger_count}")

if ledger_count > 0:
    # Show latest entry
    latest = entity.ledger_entries.latest('entry_date')
    print(f"  - Latest entry: {latest.entry_date} ({latest.entry_type}) = {latest.amount}")
    
    # Check last 6 months
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=180)
    recent_count = entity.ledger_entries.filter(entry_date__gte=start_date).count()
    print(f"  - Last 6 months: {recent_count} entries")
    
    # Show monthly breakdown
    print(f"\n  Monthly Breakdown (last 6 months):")
    from django.db.models import Sum
    monthly = entity.ledger_entries.filter(entry_date__gte=start_date).extra(
        select={'month': 'strftime("%Y-%m", entry_date)'}
    ).values('month', 'entry_type').annotate(total=Sum('amount')).order_by('month')
    
    for m in monthly:
        print(f"    {m['month']} ({m['entry_type']}): {m['total']}")
else:
    print("  ✗ WARNING: No ledger entries found!")

print("\n" + "="*60)
