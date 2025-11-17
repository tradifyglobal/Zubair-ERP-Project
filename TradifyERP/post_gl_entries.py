#!/usr/bin/env python
"""
Post GL entries for existing sample invoices
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from sales.models import Invoice
from sales.gl_integration import create_invoice_gl_entries
from accounting.models import LedgerEntry

print("\nPosting GL entries for sample invoices...\n")

# Get all invoices with status ISSUED or PAID
invoices = Invoice.objects.filter(
    status__in=['ISSUED', 'PAID', 'PARTIAL']
).order_by('invoice_number')

created_count = 0
for inv in invoices:
    # Check if GL entries already exist
    existing_entries = LedgerEntry.objects.filter(
        reference_number=inv.invoice_number
    ).count()
    
    if existing_entries == 0:
        try:
            create_invoice_gl_entries(inv)
            print(f"[OK] GL posted for {inv.invoice_number}: ${inv.total_amount:,.2f}")
            created_count += 1
        except Exception as e:
            print(f"[ERROR] Failed to post GL for {inv.invoice_number}: {str(e)}")
    else:
        print(f"[SKIP] GL already exists for {inv.invoice_number}")

print(f"\nTotal GL postings created: {created_count}")

# Verify results
gl_entries = LedgerEntry.objects.all().count()
print(f"Total GL entries in system: {gl_entries}\n")
