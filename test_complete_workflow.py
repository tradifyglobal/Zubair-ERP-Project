#!/usr/bin/env python
"""
Create a new cash receipt and test the complete workflow:
1. Create cash receipt (DRAFT)
2. Approve it (APPROVED) - should NOT create capital contribution
3. Authorize it (AUTHORIZED) - should create capital contribution and appear in reports
"""

import os
import django
from datetime import date
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings_production')
django.setup()

from accounting.models import CashReceiptLine, CapitalContribution, Entity, Account, Stakeholder, Currency

def create_and_test_new_receipt():
    """Create a new cash receipt and test the complete workflow."""
    
    print("=== CREATING NEW CASH RECEIPT FOR TESTING ===")
    
    # Get test data
    entity = Entity.objects.get(id=7)  # Testing entity
    currency = Currency.objects.get(code='INR')
    
    # Find a specific stakeholder capital account (not generic Capital account)
    capital_account = Account.objects.filter(
        entity=entity,
        name__icontains='Capital',
        name__contains='-',  # Should have account code like "3000-14"
        is_active=True
    ).first()
    
    if not capital_account:
        print("No capital account found")
        return
        
    print(f"Using Capital Account: {capital_account.name}")
    
    # Find stakeholder for this account
    # Extract name from account name (e.g., "3000-14 Nasir Ali Ali Mohammed - Capital" -> "Nasir Ali Mohammed")
    account_name = capital_account.name
    if ' - Capital' in account_name:
        name_part = account_name.split(' - Capital')[0]
        if ' ' in name_part and name_part.count(' ') >= 2:  # Has at least code + first + last name
            name_without_code = ' '.join(name_part.split(' ')[1:])  # Remove account code
            
            # Find stakeholder by name
            stakeholder = Stakeholder.objects.filter(
                entity=entity,
                status='ACTIVE',
                full_name__icontains=name_without_code.split()[0]  # Search by first name
            ).first()
        else:
            stakeholder = None
    else:
        stakeholder = None
    
    if not stakeholder:
        print(f"No stakeholder found for account: {account_name}")
        return
        
    print(f"Using Stakeholder: {stakeholder.full_name}")
    
    # Create new cash receipt
    receipt = CashReceiptLine.objects.create(
        entity=entity,
        account=capital_account,
        credit_account=capital_account,  # Same account for both debit and credit
        stakeholder=stakeholder,
        date=date.today(),
        description=f"Testing signal trigger - {stakeholder.full_name}",
        debit_amount=Decimal('15000.00'),
        credit_amount=Decimal('15000.00'),
        currency=currency,
        reference_number=f'TEST-{date.today().strftime("%Y%m%d")}',
        workflow_status='DRAFT',
        status='DRAFT',
        is_capital_contribution_posted=False
    )
    
    print(f"\n✓ Created Cash Receipt ID: {receipt.id}")
    print(f"  Amount: {receipt.debit_amount}")
    print(f"  Status: {receipt.workflow_status}")
    print(f"  Stakeholder: {receipt.stakeholder.full_name}")
    
    # Count capital contributions before
    contrib_count_before = CapitalContribution.objects.count()
    print(f"  Capital Contributions before: {contrib_count_before}")
    
    # Step 1: Approve the receipt (should NOT create capital contribution)
    print(f"\n--- STEP 1: APPROVING RECEIPT ---")
    receipt.workflow_status = 'APPROVED'
    receipt.status = 'DRAFT'
    receipt.save()
    
    contrib_count_after_approval = CapitalContribution.objects.count()
    print(f"Receipt {receipt.id} approved. Status: {receipt.workflow_status}")
    print(f"Capital Contributions after approval: {contrib_count_after_approval}")
    
    if contrib_count_after_approval == contrib_count_before:
        print("✓ CORRECT: No capital contribution created on APPROVED status")
    else:
        print("✗ UNEXPECTED: Capital contribution created on APPROVED status")
    
    # Step 2: Authorize the receipt (should create capital contribution)
    print(f"\n--- STEP 2: AUTHORIZING RECEIPT (GL POSTING) ---")
    receipt.workflow_status = 'AUTHORIZED'
    receipt.status = 'POSTED'
    receipt.save()
    
    contrib_count_after_authorization = CapitalContribution.objects.count()
    print(f"Receipt {receipt.id} authorized. Status: {receipt.workflow_status}")
    print(f"Capital Contributions after authorization: {contrib_count_after_authorization}")
    
    if contrib_count_after_authorization > contrib_count_after_approval:
        print("✓ SUCCESS: Capital contribution created on AUTHORIZED status")
        
        # Find the new capital contribution
        new_contrib = CapitalContribution.objects.filter(
            source_cash_receipt_id=receipt.id
        ).first()
        
        if new_contrib:
            print(f"\n📊 NEW CAPITAL CONTRIBUTION DETAILS:")
            print(f"  ID: {new_contrib.id}")
            print(f"  Amount: {new_contrib.amount}")
            print(f"  Status: {new_contrib.status}")
            print(f"  Workflow Status: {new_contrib.workflow_status}")
            print(f"  Is Auto Posted: {new_contrib.is_auto_posted}")
            print(f"  Source Cash Receipt: {new_contrib.source_cash_receipt_id}")
            print(f"  Stakeholder: {new_contrib.stakeholder.full_name}")
            
            print(f"\n🎯 THIS CAPITAL CONTRIBUTION SHOULD NOW APPEAR IN SHAREHOLDER REPORTS!")
            print(f"   Check: https://tradifyglobal.com/shareholder/investment-report/")
        
        # Check if receipt was marked as posted
        receipt.refresh_from_db()
        print(f"  Receipt Capital Contribution Posted: {receipt.is_capital_contribution_posted}")
        
    else:
        print("✗ FAILED: No capital contribution created on AUTHORIZED status")

if __name__ == '__main__':
    create_and_test_new_receipt()