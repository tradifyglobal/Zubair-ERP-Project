#!/usr/bin/env python
"""
Test script to verify the updated signal behavior:
- Capital contributions should now be created when cash receipt is AUTHORIZED (GL posted)
- Not when it's just APPROVED
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from accounting.models import CashReceiptLine, CapitalContribution, Entity, Account, Stakeholder
from django.utils import timezone

def test_signal_behavior():
    """Test that the signal now triggers on AUTHORIZED status."""
    
    print("=== TESTING UPDATED SIGNAL BEHAVIOR ===")
    
    # Get test entity
    entity = Entity.objects.get(id=7)  # Testing entity
    
    # Check current capital contributions
    print(f"\nCurrent capital contributions count: {CapitalContribution.objects.count()}")
    print("Last 3 auto-posted contributions:")
    for c in CapitalContribution.objects.filter(is_auto_posted=True).order_by('-id')[:3]:
        print(f"  ID: {c.id}, Amount: {c.amount}, Status: {c.status}, Workflow: {c.workflow_status}")
        print(f"    Source Receipt: {c.source_cash_receipt_id}, Created: {c.created_at}")
    
    # Check for cash receipts ready to test
    print(f"\nChecking cash receipts in APPROVED status (should NOT trigger capital contribution):")
    approved_receipts = CashReceiptLine.objects.filter(
        entity=entity, 
        workflow_status='APPROVED',
        is_capital_contribution_posted=False
    ).order_by('-id')[:3]
    
    for r in approved_receipts:
        print(f"  Receipt ID: {r.id}, Status: {r.workflow_status}, Stakeholder: {r.stakeholder_id}")
        print(f"    Amount: {r.debit_amount}, Posted: {r.is_capital_contribution_posted}")
    
    print(f"\nChecking cash receipts in AUTHORIZED status (should trigger capital contribution):")
    authorized_receipts = CashReceiptLine.objects.filter(
        entity=entity, 
        workflow_status='AUTHORIZED',
        is_capital_contribution_posted=True
    ).order_by('-id')[:3]
    
    for r in authorized_receipts:
        print(f"  Receipt ID: {r.id}, Status: {r.workflow_status}, Stakeholder: {r.stakeholder_id}")
        print(f"    Amount: {r.debit_amount}, Posted: {r.is_capital_contribution_posted}")
        
        # Check if capital contribution was created for this receipt
        cap_contrib = CapitalContribution.objects.filter(source_cash_receipt_id=r.id).first()
        if cap_contrib:
            print(f"    ✓ Capital Contribution ID: {cap_contrib.id}, Amount: {cap_contrib.amount}")
        else:
            print(f"    ✗ No capital contribution found")

if __name__ == '__main__':
    test_signal_behavior()