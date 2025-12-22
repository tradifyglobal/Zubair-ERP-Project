#!/usr/bin/env python
"""
Test the updated signal by manually triggering the authorization workflow
to verify capital contributions are created on AUTHORIZED status.
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings_production')
django.setup()

from accounting.models import CashReceiptLine, CapitalContribution, Entity
from django.utils import timezone

def test_authorization_trigger():
    """Test that capital contribution is created when receipt is authorized."""
    
    print("=== TESTING AUTHORIZATION TRIGGER ===")
    
    # Get a cash receipt in APPROVED status
    approved_receipt = CashReceiptLine.objects.filter(
        workflow_status='APPROVED',
        is_capital_contribution_posted=False,
        stakeholder__isnull=False
    ).first()
    
    if not approved_receipt:
        print("No APPROVED receipts with stakeholders found for testing")
        return
    
    print(f"Testing with Receipt ID: {approved_receipt.id}")
    print(f"  Current Status: {approved_receipt.workflow_status}")
    print(f"  Stakeholder: {approved_receipt.stakeholder_id}")
    print(f"  Amount: {approved_receipt.debit_amount}")
    print(f"  Capital Contribution Posted: {approved_receipt.is_capital_contribution_posted}")
    
    # Check if capital contribution exists before
    existing_contrib = CapitalContribution.objects.filter(
        source_cash_receipt_id=approved_receipt.id
    ).first()
    
    print(f"  Existing Capital Contribution: {existing_contrib.id if existing_contrib else 'None'}")
    
    # Count capital contributions before
    contrib_count_before = CapitalContribution.objects.count()
    print(f"\nCapital Contributions before: {contrib_count_before}")
    
    # Now simulate the authorization by changing status to AUTHORIZED
    # This should trigger the signal
    print(f"\n--- SIMULATING AUTHORIZATION ---")
    approved_receipt.workflow_status = 'AUTHORIZED'
    approved_receipt.status = 'POSTED'
    approved_receipt.save()
    
    print(f"Receipt {approved_receipt.id} status changed to: {approved_receipt.workflow_status}")
    
    # Check if capital contribution was created
    contrib_count_after = CapitalContribution.objects.count()
    print(f"Capital Contributions after: {contrib_count_after}")
    
    new_contrib = CapitalContribution.objects.filter(
        source_cash_receipt_id=approved_receipt.id
    ).first()
    
    if new_contrib:
        print(f"\n✓ SUCCESS: Capital Contribution Created!")
        print(f"  ID: {new_contrib.id}")
        print(f"  Amount: {new_contrib.amount}")
        print(f"  Status: {new_contrib.status}")
        print(f"  Workflow Status: {new_contrib.workflow_status}")
        print(f"  Is Auto Posted: {new_contrib.is_auto_posted}")
        print(f"  Source Cash Receipt: {new_contrib.source_cash_receipt_id}")
    else:
        print(f"\n✗ FAILED: No capital contribution created")
    
    # Check if the receipt was marked as posted
    approved_receipt.refresh_from_db()
    print(f"  Receipt Capital Contribution Posted: {approved_receipt.is_capital_contribution_posted}")

if __name__ == '__main__':
    test_authorization_trigger()