#!/usr/bin/env python3

import os
import sys
import django

# Add the project directory to the Python path
sys.path.append('/var/www/tradifyerp')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from accounting.models import CashPaymentLine, Entity, LedgerEntry, CapitalContribution

print("=== CHECKING CASH PAYMENT ENTRY ===")

# Check the specific cash payment entry
try:
    cash_payment = CashPaymentLine.objects.filter(reference_number='3000-11').first()
    if cash_payment:
        print(f"Cash Payment Found:")
        print(f"  ID: {cash_payment.id}")
        print(f"  Reference: {cash_payment.reference_number}")
        print(f"  Date: {cash_payment.date}")
        print(f"  Description: {cash_payment.description}")
        print(f"  Debit Account: {cash_payment.debit_account}")
        print(f"  Credit Account: {cash_payment.credit_account}")
        print(f"  Amount: {cash_payment.amount} {cash_payment.currency}")
        print(f"  Status: {cash_payment.workflow_status}")
        print(f"  Entity: {cash_payment.entity}")
        print()
        
        # Check related ledger entries
        print("=== RELATED LEDGER ENTRIES ===")
        ledger_entries = LedgerEntry.objects.filter(
            reference_number=cash_payment.reference_number
        ).order_by('account__account_number')
        
        for entry in ledger_entries:
            print(f"Account: {entry.account.account_number} - {entry.account.account_name}")
            print(f"  Debit: {entry.debit_amount}")
            print(f"  Credit: {entry.credit_amount}")
            print(f"  Description: {entry.description}")
            print(f"  Entity: {entry.entity}")
            print()
            
    else:
        print("❌ Cash Payment 3000-11 NOT FOUND")
        # Show recent cash payments
        recent_payments = CashPaymentLine.objects.all().order_by('-date')[:5]
        print("\nRecent Cash Payments:")
        for payment in recent_payments:
            print(f"  {payment.reference_number} - {payment.date} - {payment.description}")

    # Check capital contributions
    print("=== CAPITAL CONTRIBUTIONS ===")
    capital_contribs = CapitalContribution.objects.all()
    print(f"Total Capital Contributions: {capital_contribs.count()}")
    for contrib in capital_contribs:
        print(f"  {contrib.id}: {contrib.stakeholder} - {contrib.amount} - {contrib.created_at}")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()