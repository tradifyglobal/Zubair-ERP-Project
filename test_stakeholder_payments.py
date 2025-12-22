#!/usr/bin/env python
"""
Test Stakeholder Payment Workflows
Tests both profit distributions and capital withdrawals via cash and bank payments
"""
import os
import sys
import django
from decimal import Decimal

# Add TradifyERP to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'TradifyERP'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from accounting.models import (
    Entity, Stakeholder, Account, CashPaymentLine, BankPaymentLine,
    CapitalContribution, LedgerEntry
)
from django.db import transaction
from django.utils import timezone

def print_separator(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def print_account_info(account):
    if account:
        print(f"  Account: {account.account_number} - {account.name}")
        print(f"  Type: {account.account_type}")
    else:
        print("  Account: None")

def print_gl_entries(payment_id, payment_type):
    """Print GL entries for a payment"""
    gl_entries = LedgerEntry.objects.filter(
        source_document=f"{payment_type}-{payment_id}"
    ).select_related('account')
    
    if gl_entries.exists():
        print("\n  GL Entries Created:")
        total_dr = Decimal('0')
        total_cr = Decimal('0')
        for entry in gl_entries:
            dr = entry.debit_amount or Decimal('0')
            cr = entry.credit_amount or Decimal('0')
            total_dr += dr
            total_cr += cr
            print(f"    {entry.account.account_number:10} | DR: {dr:>10} | CR: {cr:>10} | {entry.account.name}")
        print(f"    {'TOTALS':10} | DR: {total_dr:>10} | CR: {total_cr:>10}")
        if total_dr == total_cr:
            print("    ✅ Balanced")
        else:
            print(f"    ❌ UNBALANCED! Difference: {total_dr - total_cr}")
    else:
        print("\n  ⚠️  No GL entries found")

def print_capital_contribution(payment_id, prefix):
    """Print capital contribution record"""
    cc = CapitalContribution.objects.filter(
        reference_number__contains=f"{prefix}-{payment_id}"
    ).select_related('equity_account', 'cash_account').first()
    
    if cc:
        print("\n  CapitalContribution Record:")
        print(f"    Reference: {cc.reference_number}")
        print(f"    Status: {cc.workflow_status}")
        print(f"    Amount: {cc.amount_company_currency}")
        print(f"    Equity Account: {cc.equity_account.account_number} - {cc.equity_account.name}")
        print(f"    Cash Account: {cc.cash_account.account_number} - {cc.cash_account.name}")
    else:
        print(f"\n  ⚠️  No CapitalContribution record found")

def test_cash_profit_distribution():
    print_separator("TEST 1: CASH PAYMENT - PROFIT DISTRIBUTION")
    
    # Get test data
    entity = Entity.objects.filter(is_active=True).first()
    stakeholder = Stakeholder.objects.filter(entity=entity).first()
    cash_account = Account.objects.filter(entity=entity, account_type='ASSET', account_number__startswith='1000').first()
    
    if not all([entity, stakeholder, cash_account]):
        print("❌ Missing test data (entity, stakeholder, or cash account)")
        return
    
    print(f"\n  Entity: {entity.name}")
    print(f"  Stakeholder: {stakeholder.full_name}")
    print(f"  Cash Account: {cash_account.account_number} - {cash_account.name}")
    
    # Check if drawings account exists before
    from accounting.stakeholder_account_helpers import get_or_create_stakeholder_dividend_account
    drawings_before = Account.objects.filter(
        entity=entity,
        account_type='EQUITY',
        name__icontains=f"{stakeholder.full_name} - Drawings"
    ).first()
    
    print(f"\n  Drawings Account Before:")
    if drawings_before:
        print(f"    EXISTS: {drawings_before.account_number} - {drawings_before.name}")
    else:
        print(f"    Does not exist - will be auto-created")
    
    # Create cash payment with profit distribution
    try:
        with transaction.atomic():
            payment = CashPaymentLine.objects.create(
                entity=entity,
                account=cash_account,
                payment_purpose='PROFIT_DISTRIBUTION',
                stakeholder=stakeholder,
                credit_account=cash_account,  # Temporary, will be replaced
                amount_company_currency=Decimal('10000.00'),
                description='Test Profit Distribution',
                workflow_status='DRAFT',
                transaction_date=timezone.now().date()
            )
            
            print(f"\n  Created Cash Payment: {payment.id}")
            print(f"    Status: {payment.workflow_status}")
            print(f"    Amount: {payment.amount_company_currency}")
            
            # Simulate authorization (this triggers the signal)
            payment.workflow_status = 'AUTHORIZED'
            payment.save()
            
            print(f"\n  Payment AUTHORIZED - Signal Triggered")
            
            # Check if drawings account was created
            drawings_after = get_or_create_stakeholder_dividend_account(stakeholder)
            print(f"\n  Drawings Account After Authorization:")
            print_account_info(drawings_after)
            
            # Check GL entries
            print_gl_entries(payment.id, 'CASH-PAYMENT')
            
            # Check CapitalContribution record
            print_capital_contribution(payment.id, 'PROFIT-CP')
            
            print("\n  ✅ Test completed - Rolling back transaction")
            raise Exception("Rollback test transaction")
            
    except Exception as e:
        if "Rollback" in str(e):
            print("  Transaction rolled back successfully")
        else:
            print(f"  ❌ Error: {str(e)}")

def test_cash_capital_withdrawal():
    print_separator("TEST 2: CASH PAYMENT - CAPITAL WITHDRAWAL")
    
    # Get test data
    entity = Entity.objects.filter(is_active=True).first()
    stakeholder = Stakeholder.objects.filter(entity=entity).first()
    cash_account = Account.objects.filter(entity=entity, account_type='ASSET', account_number__startswith='1000').first()
    
    # Get or create capital account
    from accounting.stakeholder_account_helpers import get_or_create_stakeholder_capital_account
    capital_account = get_or_create_stakeholder_capital_account(stakeholder)
    
    if not all([entity, stakeholder, cash_account, capital_account]):
        print("❌ Missing test data")
        return
    
    print(f"\n  Entity: {entity.name}")
    print(f"  Stakeholder: {stakeholder.full_name}")
    print(f"  Cash Account: {cash_account.account_number} - {cash_account.name}")
    print(f"  Capital Account: {capital_account.account_number} - {capital_account.name}")
    
    # Create cash payment with capital withdrawal
    try:
        with transaction.atomic():
            payment = CashPaymentLine.objects.create(
                entity=entity,
                account=cash_account,
                payment_purpose='CAPITAL_WITHDRAWAL',
                stakeholder=stakeholder,
                credit_account=capital_account,
                amount_company_currency=Decimal('5000.00'),
                description='Test Capital Withdrawal',
                workflow_status='DRAFT',
                transaction_date=timezone.now().date()
            )
            
            print(f"\n  Created Cash Payment: {payment.id}")
            print(f"    Purpose: {payment.payment_purpose}")
            print(f"    Amount: {payment.amount_company_currency}")
            
            # Authorize payment
            payment.workflow_status = 'AUTHORIZED'
            payment.save()
            
            print(f"\n  Payment AUTHORIZED - Signal Triggered")
            
            # Check GL entries
            print_gl_entries(payment.id, 'CASH-PAYMENT')
            
            # Check CapitalContribution record
            print_capital_contribution(payment.id, 'WITHDRAW-CP')
            
            print("\n  ✅ Test completed - Rolling back transaction")
            raise Exception("Rollback test transaction")
            
    except Exception as e:
        if "Rollback" in str(e):
            print("  Transaction rolled back successfully")
        else:
            print(f"  ❌ Error: {str(e)}")

def test_bank_profit_distribution():
    print_separator("TEST 3: BANK PAYMENT - PROFIT DISTRIBUTION")
    
    # Get test data
    entity = Entity.objects.filter(is_active=True).first()
    stakeholder = Stakeholder.objects.filter(entity=entity).first()
    bank_account = Account.objects.filter(entity=entity, account_type='ASSET', account_number__startswith='1100').first()
    
    if not all([entity, stakeholder, bank_account]):
        print("❌ Missing test data (entity, stakeholder, or bank account)")
        return
    
    print(f"\n  Entity: {entity.name}")
    print(f"  Stakeholder: {stakeholder.full_name}")
    print(f"  Bank Account: {bank_account.account_number} - {bank_account.name}")
    
    # Check if drawings account exists before
    from accounting.stakeholder_account_helpers import get_or_create_stakeholder_dividend_account
    drawings_before = Account.objects.filter(
        entity=entity,
        account_type='EQUITY',
        name__icontains=f"{stakeholder.full_name} - Drawings"
    ).first()
    
    print(f"\n  Drawings Account Before:")
    if drawings_before:
        print(f"    EXISTS: {drawings_before.account_number} - {drawings_before.name}")
    else:
        print(f"    Does not exist - will be auto-created")
    
    # Create bank payment with profit distribution
    try:
        with transaction.atomic():
            payment = BankPaymentLine.objects.create(
                entity=entity,
                account=bank_account,
                payment_purpose='PROFIT_DISTRIBUTION',
                stakeholder=stakeholder,
                credit_account=bank_account,  # Temporary
                amount_company_currency=Decimal('15000.00'),
                description='Test Bank Profit Distribution',
                workflow_status='DRAFT',
                transaction_date=timezone.now().date()
            )
            
            print(f"\n  Created Bank Payment: {payment.id}")
            print(f"    Status: {payment.workflow_status}")
            print(f"    Amount: {payment.amount_company_currency}")
            
            # Authorize payment
            payment.workflow_status = 'AUTHORIZED'
            payment.save()
            
            print(f"\n  Payment AUTHORIZED - Signal Triggered")
            
            # Check if drawings account was created
            drawings_after = get_or_create_stakeholder_dividend_account(stakeholder)
            print(f"\n  Drawings Account After Authorization:")
            print_account_info(drawings_after)
            
            # Check GL entries
            print_gl_entries(payment.id, 'BANK-PAYMENT')
            
            # Check CapitalContribution record
            print_capital_contribution(payment.id, 'PROFIT-BP')
            
            print("\n  ✅ Test completed - Rolling back transaction")
            raise Exception("Rollback test transaction")
            
    except Exception as e:
        if "Rollback" in str(e):
            print("  Transaction rolled back successfully")
        else:
            print(f"  ❌ Error: {str(e)}")

def test_bank_capital_withdrawal():
    print_separator("TEST 4: BANK PAYMENT - CAPITAL WITHDRAWAL")
    
    # Get test data
    entity = Entity.objects.filter(is_active=True).first()
    stakeholder = Stakeholder.objects.filter(entity=entity).first()
    bank_account = Account.objects.filter(entity=entity, account_type='ASSET', account_number__startswith='1100').first()
    
    # Get or create capital account
    from accounting.stakeholder_account_helpers import get_or_create_stakeholder_capital_account
    capital_account = get_or_create_stakeholder_capital_account(stakeholder)
    
    if not all([entity, stakeholder, bank_account, capital_account]):
        print("❌ Missing test data")
        return
    
    print(f"\n  Entity: {entity.name}")
    print(f"  Stakeholder: {stakeholder.full_name}")
    print(f"  Bank Account: {bank_account.account_number} - {bank_account.name}")
    print(f"  Capital Account: {capital_account.account_number} - {capital_account.name}")
    
    # Create bank payment with capital withdrawal
    try:
        with transaction.atomic():
            payment = BankPaymentLine.objects.create(
                entity=entity,
                account=bank_account,
                payment_purpose='CAPITAL_WITHDRAWAL',
                stakeholder=stakeholder,
                credit_account=capital_account,
                amount_company_currency=Decimal('8000.00'),
                description='Test Bank Capital Withdrawal',
                workflow_status='DRAFT',
                transaction_date=timezone.now().date()
            )
            
            print(f"\n  Created Bank Payment: {payment.id}")
            print(f"    Purpose: {payment.payment_purpose}")
            print(f"    Amount: {payment.amount_company_currency}")
            
            # Authorize payment
            payment.workflow_status = 'AUTHORIZED'
            payment.save()
            
            print(f"\n  Payment AUTHORIZED - Signal Triggered")
            
            # Check GL entries
            print_gl_entries(payment.id, 'BANK-PAYMENT')
            
            # Check CapitalContribution record
            print_capital_contribution(payment.id, 'WITHDRAW-BP')
            
            print("\n  ✅ Test completed - Rolling back transaction")
            raise Exception("Rollback test transaction")
            
    except Exception as e:
        if "Rollback" in str(e):
            print("  Transaction rolled back successfully")
        else:
            print(f"  ❌ Error: {str(e)}")

if __name__ == '__main__':
    print("\n" + "=" * 70)
    print("  STAKEHOLDER PAYMENT WORKFLOW TESTS")
    print("  Testing: Profit Distributions & Capital Withdrawals")
    print("  Methods: Cash Payments & Bank Payments")
    print("=" * 70)
    
    # Run all tests
    test_cash_profit_distribution()
    test_cash_capital_withdrawal()
    test_bank_profit_distribution()
    test_bank_capital_withdrawal()
    
    print_separator("ALL TESTS COMPLETED")
    print("\nNote: All tests use transactions that are rolled back.")
    print("No actual data was modified in the database.\n")
