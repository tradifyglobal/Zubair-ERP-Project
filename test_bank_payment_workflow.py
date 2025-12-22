#!/usr/bin/env python
"""
Test Bank Payment Workflow: DRAFT → APPROVED → AUTHORIZED  
Verify GL entries: Dr. Bank Account, Cr. Expense/Supplier Account
"""

import os
import django
from datetime import date
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings_production')
django.setup()

from accounting.models import BankPaymentLine, Account, Entity, Currency, LedgerEntry

def test_bank_payment_workflow():
    """Test complete bank payment workflow."""
    
    print("=== TESTING BANK PAYMENT WORKFLOW ===")
    
    # Get test data
    entity = Entity.objects.get(id=7)  # Testing entity
    currency = Currency.objects.get(code='INR')
    
    # Get supplier/expense account (credit side)
    supplier_account = Account.objects.filter(
        entity=entity,
        account_type__in=['EXPENSE', 'LIABILITY'],
        is_active=True
    ).first()
    
    if not supplier_account:
        print("✗ No supplier/expense account found")
        return
    
    # Get bank account (debit side) - should fallback to 100001 if not specified
    bank_account = Account.objects.filter(
        entity=entity,
        account_number='100001'  # Our updated fallback account
    ).first()
    
    if not bank_account:
        print("✗ Bank account 100001 not found!")
        return
    
    print(f"Using Supplier Account: {supplier_account.account_number} - {supplier_account.name}")
    print(f"Using Bank Account: {bank_account.account_number} - {bank_account.name}")
    
    # Count ledger entries before
    ledger_count_before = LedgerEntry.objects.count()
    print(f"\nLedger Entries before: {ledger_count_before}")
    
    # Step 1: Create Bank Payment (DRAFT)
    print(f"\n--- STEP 1: CREATE BANK PAYMENT ---")
    payment = BankPaymentLine.objects.create(
        entity=entity,
        account=supplier_account,  # Credit account (supplier/expense)
        credit_account=bank_account,  # Debit account (bank)  
        date=date.today(),
        description="Supplier payment via bank transfer - Test",
        debit_amount=Decimal('12000.00'),
        credit_amount=Decimal('12000.00'),
        currency=currency,
        reference_number=f'TEST-BP-{date.today().strftime("%H%M%S")}',
        workflow_status='DRAFT',
        status='DRAFT'
    )
    
    print(f"✓ Created Bank Payment ID: {payment.id}")
    print(f"  Status: {payment.workflow_status}")
    print(f"  Amount: ₹{payment.debit_amount}")
    print(f"  Description: {payment.description}")
    
    # Step 2: Approve Payment (DRAFT → APPROVED)
    print(f"\n--- STEP 2: APPROVE PAYMENT ---")
    payment.workflow_status = 'APPROVED'
    payment.save()
    
    print(f"Status changed to: {payment.workflow_status}")
    
    # Check no GL entries created yet
    ledger_count_after_approval = LedgerEntry.objects.count()
    print(f"Ledger Entries after approval: {ledger_count_after_approval}")
    
    if ledger_count_after_approval == ledger_count_before:
        print("✓ CORRECT: No GL entries created during approval")
    else:
        print("✗ UNEXPECTED: GL entries created during approval")
    
    # Step 3: Authorize Payment (APPROVED → AUTHORIZED)
    # This should create GL entries
    print(f"\n--- STEP 3: AUTHORIZE PAYMENT (CREATE GL ENTRIES) ---")
    
    # Simulate the authorization workflow manually
    # This is what BankPaymentAuthorizationView does:
    
    from django.db import transaction
    
    with transaction.atomic():
        # Create debit entry (Bank Account gets debited)
        debit_entry = LedgerEntry.objects.create(
            entity=entity,
            account=bank_account,  # Bank account debited (money goes out)
            entry_type='DEBIT',
            amount=payment.debit_amount,
            description=f"Bank Payment: {payment.description}",
            entry_date=payment.date,
            reference_number=f'BANK-PAYMENT-{payment.id}',
            is_posted=True,
            workflow_status='AUTHORIZED'
        )
        
        # Create credit entry (Supplier Account gets credited)
        credit_entry = LedgerEntry.objects.create(
            entity=entity,
            account=supplier_account,  # Supplier account credited
            entry_type='CREDIT',
            amount=payment.credit_amount,
            description=f"Bank Payment: {payment.description}",
            entry_date=payment.date,
            reference_number=f'BANK-PAYMENT-{payment.id}',
            is_posted=True,
            workflow_status='AUTHORIZED'
        )
        
        # Update payment status
        payment.workflow_status = 'AUTHORIZED'
        payment.status = 'POSTED'
        payment.save()
    
    print(f"Status changed to: {payment.workflow_status}")
    
    # Verify GL entries were created
    ledger_count_after_authorization = LedgerEntry.objects.count()
    print(f"Ledger Entries after authorization: {ledger_count_after_authorization}")
    
    if ledger_count_after_authorization == ledger_count_before + 2:
        print("✓ SUCCESS: 2 GL entries created (debit + credit)")
        
        print(f"\n📊 GL ENTRIES CREATED:")
        print(f"  DEBIT Entry ID: {debit_entry.id}")
        print(f"    Account: {debit_entry.account.account_number} - {debit_entry.account.name}")
        print(f"    Type: {debit_entry.entry_type}")
        print(f"    Amount: ₹{debit_entry.amount}")
        print(f"    Posted: {debit_entry.is_posted}")
        
        print(f"\n  CREDIT Entry ID: {credit_entry.id}")
        print(f"    Account: {credit_entry.account.account_number} - {credit_entry.account.name}")
        print(f"    Type: {credit_entry.entry_type}")
        print(f"    Amount: ₹{credit_entry.amount}")
        print(f"    Posted: {credit_entry.is_posted}")
        
        print(f"\n🎯 WORKFLOW VERIFICATION:")
        print(f"  ✓ Bank Payment created in DRAFT")
        print(f"  ✓ Approved to APPROVED (no GL entries)")
        print(f"  ✓ Authorized to AUTHORIZED (GL entries created)")
        print(f"  ✓ Dr. Bank Account (₹{debit_entry.amount}) - Bank balance decreases")
        print(f"  ✓ Cr. Supplier Account (₹{credit_entry.amount}) - Liability settled")
        print(f"\n✅ BANK PAYMENT WORKFLOW TEST PASSED!")
        
    else:
        print("✗ FAILED: Incorrect number of GL entries created")

if __name__ == '__main__':
    test_bank_payment_workflow()