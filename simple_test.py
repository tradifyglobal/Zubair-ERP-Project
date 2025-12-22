#!/usr/bin/env python
"""
Simple test: Create cash receipt and verify signal triggers on AUTHORIZED status.
"""

import os
import django
from datetime import date
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings_production')
django.setup()

from accounting.models import CashReceiptLine, CapitalContribution, Entity, Account, Stakeholder, Currency

def simple_test():
    """Simple test with known data."""
    
    print("=== SIMPLE SIGNAL TEST ===")
    
    # Use known entities
    entity = Entity.objects.get(id=7)
    stakeholder = Stakeholder.objects.get(id=15)  # Sajaz Ahmed
    account = Account.objects.get(id=91959)  # Sajaz Ahmed - Capital
    currency = Currency.objects.get(code='INR')
    
    print(f"Entity: {entity.name}")
    print(f"Stakeholder: {stakeholder.full_name}")
    print(f"Account: {account.name}")
    
    # Count capital contributions before
    contrib_count_before = CapitalContribution.objects.count()
    print(f"\nCapital Contributions before: {contrib_count_before}")
    
    # Create new cash receipt
    receipt = CashReceiptLine.objects.create(
        entity=entity,
        account=account,
        credit_account=account,
        stakeholder=stakeholder,
        date=date.today(),
        description=f"Signal test - {stakeholder.full_name}",
        debit_amount=Decimal('25000.00'),
        credit_amount=Decimal('25000.00'),
        currency=currency,
        reference_number=f'SIGNAL-TEST-{date.today().strftime("%H%M%S")}',
        workflow_status='DRAFT',
        status='DRAFT',
        is_capital_contribution_posted=False
    )
    
    print(f"\n✓ Created Cash Receipt ID: {receipt.id}")
    print(f"  Status: {receipt.workflow_status}")
    print(f"  Amount: {receipt.debit_amount}")
    
    # Test 1: Move to APPROVED (should NOT create capital contribution)
    print(f"\n--- TEST 1: APPROVE (should NOT create capital contribution) ---")
    receipt.workflow_status = 'APPROVED'
    receipt.save()
    
    contrib_count_after_approval = CapitalContribution.objects.count()
    print(f"Status: {receipt.workflow_status}")
    print(f"Capital Contributions: {contrib_count_after_approval}")
    
    if contrib_count_after_approval == contrib_count_before:
        print("✓ PASS: No capital contribution created on APPROVED")
    else:
        print("✗ FAIL: Capital contribution created on APPROVED")
    
    # Test 2: Move to AUTHORIZED (should create capital contribution)
    print(f"\n--- TEST 2: AUTHORIZE (should create capital contribution) ---")
    receipt.workflow_status = 'AUTHORIZED'
    receipt.status = 'POSTED'
    receipt.save()
    
    contrib_count_after_authorization = CapitalContribution.objects.count()
    print(f"Status: {receipt.workflow_status}")
    print(f"Capital Contributions: {contrib_count_after_authorization}")
    
    if contrib_count_after_authorization > contrib_count_before:
        print("✓ PASS: Capital contribution created on AUTHORIZED")
        
        # Find the new capital contribution
        new_contrib = CapitalContribution.objects.filter(
            source_cash_receipt_id=receipt.id
        ).first()
        
        if new_contrib:
            print(f"\n📊 CAPITAL CONTRIBUTION CREATED:")
            print(f"  ID: {new_contrib.id}")
            print(f"  Amount: {new_contrib.amount}")
            print(f"  Status: {new_contrib.status}")
            print(f"  Stakeholder: {new_contrib.stakeholder.full_name}")
            print(f"  Is Auto Posted: {new_contrib.is_auto_posted}")
            
            print(f"\n🎯 SUCCESS! Capital contribution should now appear in shareholder reports!")
            print(f"   https://tradifyglobal.com/shareholder/investment-report/")
        else:
            print("✗ ERROR: Capital contribution should exist but not found")
    else:
        print("✗ FAIL: No capital contribution created on AUTHORIZED")
    
    # Check receipt status
    receipt.refresh_from_db()
    print(f"\nReceipt Posted Flag: {receipt.is_capital_contribution_posted}")

if __name__ == '__main__':
    simple_test()