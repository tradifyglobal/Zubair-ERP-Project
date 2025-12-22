#!/usr/bin/env python
"""
Clean up and create proper hierarchical accounts for INT-005.
"""

from decimal import Decimal
from django.db import transaction
from accounting.models import Entity, Account, Currency, CapitalContribution, Stakeholder

# Delete bad accounts first
print("Cleaning up bad hierarchical accounts...")
bad_accts = Account.objects.filter(
    entity__entity_code='INT-005',
    account_number__startswith='3100-'
)
count = bad_accts.count()
if count > 0:
    bad_accts.delete()
    print(f"✓ Deleted {count} bad accounts")
else:
    print("No bad accounts to delete")

# Show remaining
remaining = Account.objects.filter(entity__entity_code='INT-005', account_number__startswith='3100')
print(f"\nRemaining 3100 accounts: {remaining.count()}")
for a in remaining.order_by('account_number'):
    print(f"  {a.account_number} - {a.name}")

print(f"\nTotal accounts in system: {Account.objects.count()}")
