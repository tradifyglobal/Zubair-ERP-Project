#!/usr/bin/env python
import os
import sys

# Add the project directory to the path
sys.path.insert(0, '/var/www/tradifyerp')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings_production')

import django
django.setup()

from accounting.models import CapitalContribution, CashReceiptLine, BankReceiptLine
from django.db import connection

print("\n" + "="*120)
print("MIGRATION STATUS")
print("="*120)

# Get applied migrations
with connection.cursor() as cursor:
    cursor.execute("SELECT app, name FROM django_migrations WHERE app='accounting' ORDER BY name DESC LIMIT 10;")
    rows = cursor.fetchall()
    print("\nApplied Migrations (Last 10):")
    for row in rows:
        print(f"  {row[0]}: {row[1]}")

# Check if stakeholder column exists
with connection.cursor() as cursor:
    try:
        cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name='accounting_cashreceiptline' AND column_name='stakeholder_id';")
        result = cursor.fetchone()
        if result:
            print("\n✓ stakeholder_id column EXISTS on cashreceiptline")
        else:
            print("\n✗ stakeholder_id column NOT FOUND on cashreceiptline - MIGRATION NOT APPLIED!")
    except Exception as e:
        print(f"\n✗ Error checking column: {str(e)}")

print("\n" + "="*120)
print("CAPITAL CONTRIBUTIONS CHECK")
print("="*120)
print("CAPITAL CONTRIBUTIONS CHECK")
print("="*120)

contributions = CapitalContribution.objects.all().order_by('-id')[:20]

print("\nCapital Contributions (Last 20):")
print("-" * 120)
print(f"{'ID':<5} {'Stakeholder':<25} {'Amount':<15} {'Status':<15} {'Workflow':<20} {'Auto Posted':<12}")
print("-" * 120)

if contributions.exists():
    for cc in contributions:
        stakeholder_name = cc.stakeholder.name if cc.stakeholder else "N/A"
        amount = cc.amount_company_currency if cc.amount_company_currency else cc.amount if cc.amount else 0
        print(f"{cc.id:<5} {stakeholder_name:<25} {amount:<15} {cc.status:<15} {cc.workflow_status:<20} {str(cc.is_auto_posted):<12}")
else:
    print("No capital contributions found")

print("-" * 120)
print(f"\nTotal records: {CapitalContribution.objects.count()}")
print(f"Approved: {CapitalContribution.objects.filter(workflow_status='APPROVED').count()}")
print(f"Auto-posted: {CapitalContribution.objects.filter(is_auto_posted=True).count()}")

# Check if there are any pending receipts
print("\n" + "="*120)
print("CASH RECEIPT LINES (for capital)")
print("="*120)

cash_receipts = CashReceiptLine.objects.filter(stakeholder__isnull=False).order_by('-date')[:10]
print(f"\nCash Receipt Lines with stakeholder (Last 10):")
print("-" * 120)
print(f"{'ID':<5} {'Date':<12} {'Stakeholder':<25} {'Amount':<15} {'Workflow Status':<20} {'Posted':<12}")
print("-" * 120)

if cash_receipts.exists():
    for line in cash_receipts:
        stakeholder_name = line.stakeholder.name if line.stakeholder else "N/A"
        print(f"{line.id:<5} {str(line.date):<12} {stakeholder_name:<25} {line.debit_amount:<15} {line.workflow_status:<20} {str(line.is_capital_contribution_posted):<12}")
else:
    print("No cash receipts with stakeholder found")

# Check if there are any pending receipts that haven't been posted
print("\n" + "="*120)
print("PENDING CAPITAL RECEIPTS (Ready to be posted)")
print("="*120)

pending = CashReceiptLine.objects.filter(
    stakeholder__isnull=False,
    workflow_status='APPROVED',
    is_capital_contribution_posted=False
).order_by('-date')[:10]

print(f"\nPending Cash Receipts not yet posted (Last 10):")
if pending.exists():
    print("-" * 120)
    print(f"{'ID':<5} {'Date':<12} {'Stakeholder':<25} {'Amount':<15} {'Status':<15}")
    print("-" * 120)
    for line in pending:
        stakeholder_name = line.stakeholder.name if line.stakeholder else "N/A"
        print(f"{line.id:<5} {str(line.date):<12} {stakeholder_name:<25} {line.debit_amount:<15} {line.workflow_status:<15}")
else:
    print("No pending cash receipts found")

# Check bank receipts too
print("\n" + "="*120)
print("BANK RECEIPT LINES (for capital)")
print("="*120)

bank_receipts = BankReceiptLine.objects.filter(stakeholder__isnull=False).order_by('-date')[:10]
print(f"\nBank Receipt Lines with stakeholder (Last 10):")
print("-" * 120)
print(f"{'ID':<5} {'Date':<12} {'Stakeholder':<25} {'Amount':<15} {'Workflow Status':<20} {'Posted':<12}")
print("-" * 120)

if bank_receipts.exists():
    for line in bank_receipts:
        stakeholder_name = line.stakeholder.name if line.stakeholder else "N/A"
        print(f"{line.id:<5} {str(line.date):<12} {stakeholder_name:<25} {line.debit_amount:<15} {line.workflow_status:<20} {str(line.is_capital_contribution_posted):<12}")
else:
    print("No bank receipts with stakeholder found")

print("\n" + "="*120)
