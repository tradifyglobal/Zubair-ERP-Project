#!/usr/bin/env python3
"""
Investigate the ₹200,000 discrepancy between:
- Completed Contributions: 12 items, ₹3,200,000.00
- Current Cash Balance: 2 accounts, ₹3,000,000.00
"""

import os
import django
import sys
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
sys.path.insert(0, '/var/www/tradifyerp')
django.setup()

from accounting.models import CapitalContribution, Account, LedgerEntry, Entity, CashReceiptLine
from django.db.models import Sum, Q

# Get the current entity (Pristine Planet)
entity = Entity.objects.filter(name__icontains='Pristine').first()
if not entity:
    print("Error: Could not find entity")
    sys.exit(1)

print(f"Entity: {entity.name} (ID: {entity.id})")
print("=" * 80)

# ============================================================================
# PART 1: COMPLETED CONTRIBUTIONS
# ============================================================================
print("\n1. COMPLETED CONTRIBUTIONS")
print("-" * 80)

completed = CapitalContribution.objects.filter(
    entity=entity,
    status='COMPLETED'
).select_related('stakeholder', 'currency')

print(f"Total completed contributions: {completed.count()}")
total_completed = Decimal('0')

for idx, contrib in enumerate(completed, 1):
    amount = Decimal(str(contrib.amount_company_currency or 0))
    total_completed += amount
    print(f"  {idx:2d}. {contrib.stakeholder.full_name:25s} | {contrib.currency.code:3s} {amount:15,.2f} | Date: {contrib.contribution_date}")

print(f"\nTotal Completed Contributions: ₹{total_completed:,.2f}")

# ============================================================================
# PART 2: CASH ACCOUNTS
# ============================================================================
print("\n2. CASH ACCOUNTS & BALANCES")
print("-" * 80)

cash_accounts = Account.objects.filter(
    entity=entity,
    account_type='ASSET'
).filter(
    Q(name__icontains='cash') | 
    Q(name__icontains='bank') | 
    Q(account_number__startswith='100')
).order_by('name')

print(f"Total cash accounts found: {cash_accounts.count()}")
print()

total_cash_balance = Decimal('0')
for account in cash_accounts:
    debits = LedgerEntry.objects.filter(
        account=account, entry_type='DEBIT', is_posted=True
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
    
    credits = LedgerEntry.objects.filter(
        account=account, entry_type='CREDIT', is_posted=True
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
    
    balance = Decimal(str(debits)) - Decimal(str(credits))
    total_cash_balance += balance
    
    print(f"Account: {account.name} ({account.account_number})")
    print(f"  Debits:  ₹{debits:,.2f}")
    print(f"  Credits: ₹{credits:,.2f}")
    print(f"  Balance: ₹{balance:,.2f}")
    print()

print(f"Total Cash Balance: ₹{total_cash_balance:,.2f}")

# ============================================================================
# PART 3: DISCREPANCY
# ============================================================================
print("\n3. DISCREPANCY ANALYSIS")
print("-" * 80)

discrepancy = total_completed - total_cash_balance
print(f"Completed Contributions: ₹{total_completed:,.2f}")
print(f"Current Cash Balance:    ₹{total_cash_balance:,.2f}")
print(f"Discrepancy:             ₹{discrepancy:,.2f}")

# ============================================================================
# PART 4: CASH RECEIPTS - Check if posted
# ============================================================================
print("\n4. CASH RECEIPTS STATUS")
print("-" * 80)

cash_receipts = CashReceiptLine.objects.filter(
    entity=entity
).select_related('stakeholder').order_by('created_at')

print(f"Total cash receipts: {cash_receipts.count()}")
print()

for receipt in cash_receipts:
    amount = Decimal(str(receipt.debit_amount or 0))
    print(f"Receipt: {receipt.reference_number or 'N/A'}")
    print(f"  Stakeholder: {receipt.stakeholder.full_name if receipt.stakeholder else 'N/A'}")
    print(f"  Debit Amount: ₹{amount:,.2f}")
    print(f"  Status: {receipt.status}")
    print(f"  Workflow Status: {receipt.workflow_status}")
    print()

# ============================================================================
# PART 5: UNPOSTED/DRAFT ITEMS
# ============================================================================
print("\n5. DRAFT/UNPOSTED CASH RECEIPTS")
print("-" * 80)

draft_receipts = CashReceiptLine.objects.filter(
    entity=entity,
    status='DRAFT'
)

print(f"Total DRAFT receipts: {draft_receipts.count()}")
unposted_total = Decimal('0')

for receipt in draft_receipts:
    amount = Decimal(str(receipt.debit_amount or 0))
    unposted_total += amount
    print(f"  {receipt.reference_number or 'N/A':20s} | ₹{amount:15,.2f} | Status: {receipt.status}")

if unposted_total > 0:
    print(f"\nTotal DRAFT Amount: ₹{unposted_total:,.2f}")
else:
    print("No draft receipts found")

# ============================================================================
# PART 6: LEDGER ENTRIES FROM CAPITAL CONTRIBUTIONS
# ============================================================================
print("\n6. CAPITAL CONTRIBUTION POSTINGS (from GL)")
print("-" * 80)

# Find all equity accounts related to shareholders
equity_accounts = Account.objects.filter(
    entity=entity,
    account_type='EQUITY'
).filter(
    Q(account_number__startswith='SHR-') |
    Q(name__iendswith=' - Capital')
).order_by('name')

print(f"Found {equity_accounts.count()} shareholder equity accounts")
equity_total = Decimal('0')

for account in equity_accounts:
    debits = LedgerEntry.objects.filter(
        account=account, entry_type='DEBIT', is_posted=True
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
    
    credits = LedgerEntry.objects.filter(
        account=account, entry_type='CREDIT', is_posted=True
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
    
    balance = Decimal(str(credits)) - Decimal(str(debits))  # EQUITY balance = CR - DR
    equity_total += balance
    
    if balance != 0:
        print(f"\n{account.name}:")
        print(f"  Debits:  ₹{debits:,.2f}")
        print(f"  Credits: ₹{credits:,.2f}")
        print(f"  Balance: ₹{balance:,.2f}")

print(f"\nTotal from Equity Accounts: ₹{equity_total:,.2f}")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"Completed Contributions (DB records): ₹{total_completed:,.2f}")
print(f"Cash Balance (GL postings):            ₹{total_cash_balance:,.2f}")
print(f"Equity Accounts (GL postings):         ₹{equity_total:,.2f}")
print(f"Unposted Receipts:                     ₹{unposted_total:,.2f}")
print(f"Discrepancy:                           ₹{discrepancy:,.2f}")
print()

if discrepancy > 0:
    print("⚠️  ANALYSIS: More contributions recorded than cash received")
    print(f"   Likely cause: {unposted_total:,.2f} in unposted receipts")
    if unposted_total >= discrepancy:
        print("   ✓ Unposted receipts explain the discrepancy")
    else:
        print(f"   ✗ Unposted receipts only explain ₹{unposted_total:,.2f}")
        print(f"   Remaining gap: ₹{discrepancy - unposted_total:,.2f}")
elif discrepancy < 0:
    print("⚠️  ANALYSIS: More cash received than contributions recorded")
    print(f"   This could indicate duplicate postings or incorrect GL entries")
else:
    print("✓ No discrepancy - all amounts match perfectly")
