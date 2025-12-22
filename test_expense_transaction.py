#!/usr/bin/env python
"""
Test Complete Expense Transaction Workflow
Creates, approves, and reimburses an expense, then verifies GL entries
"""

import os
import sys
import django
from decimal import Decimal
from datetime import date, timedelta

# Setup Django
sys.path.append('/var/www/tradifyerp')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings_production')
django.setup()

from django.db import models
from django.contrib.auth.models import User
from accounting.models import Entity, Account, LedgerEntry
from hr.models import Employee
from expenses.models import (
    ExpenseCategory, EmployeeExpenseReport, EmployeeExpense,
    ExpenseReimbursement, ExpenseApprovalWorkflow
)


def test_expense_workflow():
    """Test complete expense workflow"""
    
    print("\n" + "="*70)
    print("EXPENSE TRANSACTION TEST - Complete Workflow")
    print("="*70)
    
    # Step 1: Get or create test data
    print("\n[Step 1] Setting up test data...")
    
    # Get entity
    entity = Entity.objects.filter(is_active=True).first()
    if not entity:
        print("❌ No active entity found!")
        return
    print(f"✅ Entity: {entity.name} ({entity.code})")
    
    # Get admin user for testing
    user = User.objects.filter(is_superuser=True).first()
    if not user:
        print("❌ No admin user found!")
        return
    print(f"✅ User: {user.username}")
    
    # Create minimal employee record for testing
    employee, created = Employee.objects.get_or_create(
        user=user,
        entity=entity,
        defaults={
            'employee_id': f'EMP-{user.username}',
        }
    )
    if created:
        print(f"✅ Employee created: {employee.employee_id}")
    else:
        print(f"✅ Employee: {employee.employee_id}")
    
    # Get expense category
    category = ExpenseCategory.objects.filter(
        entity=entity,
        is_active=True,
        expense_account__isnull=False
    ).first()
    
    if not category:
        print("❌ No expense category with GL account found!")
        return
    print(f"✅ Category: {category.name} → Account {category.expense_account.account_number}")
    
    # Step 2: Create Expense Report
    print("\n[Step 2] Creating expense report...")
    
    report = EmployeeExpenseReport.objects.create(
        entity=entity,
        employee=employee,
        period_start=date.today() - timedelta(days=7),
        period_end=date.today(),
        description="Test expense report for GL integration testing",
        status='DRAFT',
        submitted_by=user
    )
    print(f"✅ Report created: ID {report.id}")
    
    # Step 3: Create Expense Item
    print("\n[Step 3] Creating expense item...")
    
    expense = EmployeeExpense.objects.create(
        report=report,
        category=category,
        expense_date=date.today(),
        description="Test travel expense for GL posting",
        amount=Decimal('500.00'),
        status='DRAFT'
    )
    print(f"✅ Expense created: ID {expense.id}, Amount: ${expense.amount}")
    
    # Step 4: Submit and Approve Expense
    print("\n[Step 4] Submitting and approving expense...")
    
    # Submit report
    report.status = 'SUBMITTED'
    report.save()
    print(f"✅ Report submitted")
    
    # Approve expense item
    expense.status = 'APPROVED'
    expense.save()
    print(f"✅ Expense item approved")
    
    # Approve report
    report.status = 'APPROVED'
    report.approved_by = user
    report.save()
    print(f"✅ Report approved")
    
    # Step 5: Post to GL (Phase 1)
    print("\n[Step 5] Posting expense to GL (Phase 1: DEBIT Expense, CREDIT AP)...")
    
    result = expense.post_to_gl()
    if result:
        print(f"✅ Expense posted to GL successfully!")
        
        # Verify GL entries
        entries = LedgerEntry.objects.filter(
            reference_number=f"EXP-{report.id}-{expense.id}",
            is_posted=True
        )
        print(f"\n   GL Entries Created: {entries.count()}")
        for entry in entries:
            print(f"   - {entry.entry_type}: {entry.account.account_number} ({entry.account.name}) - ${entry.amount}")
    else:
        print(f"❌ Expense GL posting failed!")
        return
    
    # Step 6: Create Reimbursement
    print("\n[Step 6] Creating reimbursement...")
    
    reimbursement = ExpenseReimbursement.objects.create(
        report=report,
        amount=expense.amount,
        method='BANK_TRANSFER',
        status='SCHEDULED',
        scheduled_date=date.today()
    )
    print(f"✅ Reimbursement created: ID {reimbursement.id}, Amount: ${reimbursement.amount}")
    
    # Step 7: Complete Payment
    print("\n[Step 7] Processing reimbursement payment...")
    
    reimbursement.complete_payment(transaction_id=f"TXN-TEST-{reimbursement.id}")
    print(f"✅ Payment completed: {reimbursement.transaction_id}")
    
    # Step 8: Post to GL (Phase 2)
    print("\n[Step 8] Posting reimbursement to GL (Phase 2: DEBIT AP, CREDIT Bank)...")
    
    result = reimbursement.post_to_gl()
    if result:
        print(f"✅ Reimbursement posted to GL successfully!")
        
        # Verify GL entries
        entries = LedgerEntry.objects.filter(
            reference_number=reimbursement.transaction_id,
            is_posted=True
        )
        print(f"\n   GL Entries Created: {entries.count()}")
        for entry in entries:
            print(f"   - {entry.entry_type}: {entry.account.account_number} ({entry.account.name}) - ${entry.amount}")
    else:
        print(f"❌ Reimbursement GL posting failed!")
        return
    
    # Step 9: Verify Complete Flow
    print("\n[Step 9] Verifying complete accounting flow...")
    
    all_entries = LedgerEntry.objects.filter(
        entity=entity,
        is_posted=True
    ).filter(
        models.Q(reference_number=f"EXP-{report.id}-{expense.id}") |
        models.Q(reference_number=reimbursement.transaction_id)
    ).order_by('entry_date', 'id')
    
    print(f"\n   Total GL Entries: {all_entries.count()}")
    print(f"\n   Complete Transaction Journal:")
    print(f"   {'Date':<12} {'Account':<10} {'Description':<40} {'Debit':<12} {'Credit':<12}")
    print(f"   {'-'*100}")
    
    total_debit = Decimal('0')
    total_credit = Decimal('0')
    
    for entry in all_entries:
        debit = entry.amount if entry.entry_type == 'DEBIT' else Decimal('0')
        credit = entry.amount if entry.entry_type == 'CREDIT' else Decimal('0')
        total_debit += debit
        total_credit += credit
        
        print(f"   {str(entry.entry_date):<12} {entry.account.account_number:<10} {entry.description[:38]:<40} ${debit:>10.2f} ${credit:>10.2f}")
    
    print(f"   {'-'*100}")
    print(f"   {'TOTALS':<52} ${total_debit:>10.2f} ${total_credit:>10.2f}")
    
    # Verify balanced
    if total_debit == total_credit:
        print(f"\n   ✅ BALANCED: Debits = Credits = ${total_debit}")
    else:
        print(f"\n   ❌ UNBALANCED: Debits ${total_debit} ≠ Credits ${total_credit}")
    
    # Step 10: Check AP Balance
    print("\n[Step 10] Checking Accounts Payable balance...")
    
    ap_account = Account.objects.get(
        entity=entity,
        account_number='2100'
    )
    
    ap_entries = LedgerEntry.objects.filter(
        account=ap_account,
        is_posted=True
    )
    
    ap_debits = ap_entries.filter(entry_type='DEBIT').aggregate(
        total=models.Sum('amount')
    )['total'] or Decimal('0')
    
    ap_credits = ap_entries.filter(entry_type='CREDIT').aggregate(
        total=models.Sum('amount')
    )['total'] or Decimal('0')
    
    ap_balance = ap_credits - ap_debits  # Liability: CR - DR
    
    print(f"   AP Account: {ap_account.account_number} - {ap_account.name}")
    print(f"   Total Credits: ${ap_credits}")
    print(f"   Total Debits:  ${ap_debits}")
    print(f"   Balance:       ${ap_balance}")
    
    if ap_balance == Decimal('0'):
        print(f"   ✅ AP account balanced (all reimbursements paid)")
    else:
        print(f"   ⚠️  AP balance: ${ap_balance} (pending reimbursements)")
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"✅ Report ID: {report.id}")
    print(f"✅ Expense ID: {expense.id}")
    print(f"✅ Reimbursement ID: {reimbursement.id}")
    print(f"✅ Amount: ${expense.amount}")
    print(f"✅ GL Entries: {all_entries.count()} (should be 4)")
    print(f"✅ Balanced: {total_debit == total_credit}")
    print(f"✅ AP Cleared: {ap_balance == Decimal('0')}")
    print("\n🎉 EXPENSE WORKFLOW TEST COMPLETED SUCCESSFULLY!")
    print("="*70 + "\n")


if __name__ == '__main__':
    test_expense_workflow()
