#!/usr/bin/env python3
"""
Delete all test cash receipt entries and reset sequence
"""
import os
import django
import sys
from decimal import Decimal

# Add the project directory to the Python path
sys.path.append('/var/www/tradifyerp')

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')

# Setup Django
django.setup()

# Import models
from accounting.models import CashReceiptLine, LedgerEntry
from django.db import connection
from datetime import date

print("DELETING ALL TEST CASH RECEIPT ENTRIES")
print("=====================================")

# Define the test entries to delete based on their characteristics
test_entries = [
    {"description": "Test", "amount": Decimal('100.00'), "date": date(2025, 12, 17)},
    {"description": "Test after fix", "amount": Decimal('100000.00'), "date": date(2025, 12, 17)},
    {"description": "TEST Cash Receipt - After Fixes", "amount": Decimal('50000.00'), "date": date(2025, 12, 16)},
    {"description": "WEB AUTHORIZATION TEST - Ready for Authorization", "amount": Decimal('15000.00'), "date": date(2025, 12, 16)},
    {"description": "AUTHORIZATION TEST - Draft Receipt", "amount": Decimal('25000.00'), "date": date(2025, 12, 16)},
]

deleted_count = 0
total_ledger_deleted = 0

print("1. SEARCHING AND DELETING TEST ENTRIES...")

for entry_info in test_entries:
    # Find matching cash receipts
    receipts = CashReceiptLine.objects.filter(
        description__icontains=entry_info["description"],
        debit_amount=entry_info["amount"],
        date=entry_info["date"]
    )
    
    print(f"\nSearching for: {entry_info['description']} - {entry_info['amount']} on {entry_info['date']}")
    print(f"Found {receipts.count()} matching entries")
    
    for receipt in receipts:
        print(f"  - Deleting receipt ID: {receipt.id}")
        print(f"    Description: {receipt.description}")
        print(f"    Amount: {receipt.debit_amount} {receipt.currency}")
        print(f"    Status: {receipt.workflow_status}")
        
        # Find and delete related ledger entries
        related_ledger = LedgerEntry.objects.filter(
            entity=receipt.entity,
            entry_date=receipt.date,
            description__icontains=receipt.description.split()[0]  # Use first word for matching
        )
        
        if related_ledger.exists():
            ledger_count = related_ledger.count()
            print(f"    - Deleting {ledger_count} related ledger entries")
            related_ledger.delete()
            total_ledger_deleted += ledger_count
        
        # Delete the cash receipt
        receipt.delete()
        deleted_count += 1
        print(f"    ✅ Deleted receipt ID {receipt.id}")

print(f"\n2. DELETION SUMMARY...")
print(f"Cash receipts deleted: {deleted_count}")
print(f"Ledger entries deleted: {total_ledger_deleted}")

# Reset the sequence for CashReceiptLine
print(f"\n3. RESETTING SEQUENCE...")

try:
    with connection.cursor() as cursor:
        # Get the current maximum ID
        cursor.execute("SELECT MAX(id) FROM accounting_cashreceiptline")
        max_id = cursor.fetchone()[0]
        
        if max_id is None:
            max_id = 0
        
        print(f"Current maximum ID: {max_id}")
        
        # Reset the sequence to start from the next number
        next_id = max_id + 1
        cursor.execute(f"ALTER SEQUENCE accounting_cashreceiptline_id_seq RESTART WITH {next_id}")
        print(f"✅ Reset sequence to start from: {next_id}")
        
except Exception as e:
    print(f"❌ Error resetting sequence: {e}")

# Verify deletion
print(f"\n4. VERIFICATION...")
remaining_test_entries = CashReceiptLine.objects.filter(
    description__iregex=r'(test|authorization|after fixes)'
)

print(f"Remaining test entries: {remaining_test_entries.count()}")

if remaining_test_entries.exists():
    print("Still found:")
    for entry in remaining_test_entries:
        print(f"  - ID {entry.id}: {entry.description} - {entry.debit_amount}")
else:
    print("✅ All test entries successfully removed")

# Show current cash receipts count
total_receipts = CashReceiptLine.objects.count()
print(f"Total remaining cash receipts: {total_receipts}")

print(f"\n✅ CLEANUP COMPLETE!")
print("All test entries have been deleted and sequence has been reset.")