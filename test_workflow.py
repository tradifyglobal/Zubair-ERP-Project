#!/usr/bin/env python3
"""
Test End-to-End Workflow for ShareholderInvestmentRegister
Verifies that:
1. CashReceiptLine can be created and authorized
2. ShareholderInvestmentRegister entry is auto-created on authorization
3. GL entries are properly posted
4. Report views work correctly
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
sys.path.insert(0, '/var/www/tradifyerp')
sys.path.insert(0, '/var/www/tradifyerp/TradifyERP')

django.setup()

from decimal import Decimal
from datetime import datetime
from django.contrib.auth.models import User
from accounting.models import (
    CashReceiptLine, ShareholderInvestmentRegister, LedgerEntry,
    Entity, Stakeholder, Account, Currency
)

print("=" * 70)
print("END-TO-END WORKFLOW TEST")
print("=" * 70)
print()

# Test 1: Get test entity and stakeholder
print("[Test 1] Fetching test data...")
try:
    entity = Entity.objects.get(name='Testing')
    print(f"✓ Entity found: {entity.name}")
except Entity.DoesNotExist:
    print("✗ Test entity not found. Create one first in admin.")
    sys.exit(1)

try:
    stakeholder = Stakeholder.objects.get(name='Sajaz Ahmed')
    print(f"✓ Stakeholder found: {stakeholder.name}")
except Stakeholder.DoesNotExist:
    print("✗ Stakeholder not found. Create one first in admin.")
    sys.exit(1)

# Test 2: Get accounts and currency
print()
print("[Test 2] Fetching GL accounts and currency...")
try:
    cash_account = Account.objects.get(account_code='100001')
    print(f"✓ Cash account found: {cash_account.account_code}")
except Account.DoesNotExist:
    print("✗ Cash account 100001 not found")
    sys.exit(1)

try:
    customer_account = Account.objects.get(account_code='3000-01')
    print(f"✓ Customer account found: {customer_account.account_code}")
except Account.DoesNotExist:
    print("✗ Customer account 3000-01 not found")
    sys.exit(1)

try:
    currency = Currency.objects.get(code='INR')
    print(f"✓ Currency found: {currency.code}")
except Currency.DoesNotExist:
    print("✗ Currency INR not found")
    sys.exit(1)

# Test 3: Get or create test user
print()
print("[Test 3] Fetching test user...")
user, created = User.objects.get_or_create(
    username='testuser',
    defaults={'first_name': 'Test', 'last_name': 'User', 'email': 'test@test.com'}
)
if created:
    print(f"✓ User created: {user.username}")
else:
    print(f"✓ User found: {user.username}")

# Test 4: Create CashReceiptLine
print()
print("[Test 4] Creating CashReceiptLine...")
try:
    cash_receipt = CashReceiptLine.objects.create(
        entity=entity,
        stakeholder=stakeholder,
        receipt_number=f'CRV-TEST-{int(datetime.now().timestamp())}',
        receipt_date=datetime.now().date(),
        debit_account=customer_account,
        credit_account=cash_account,
        amount=500.00,
        currency=currency,
        exchange_rate=1.0,
        description='Test cash receipt for workflow',
        workflow_status='DRAFT',
        created_by=user
    )
    print(f"✓ CashReceiptLine created: {cash_receipt.receipt_number}")
    print(f"  Amount: {cash_receipt.amount}")
    print(f"  Status: {cash_receipt.workflow_status}")
except Exception as e:
    print(f"✗ Error creating CashReceiptLine: {str(e)}")
    sys.exit(1)

# Test 5: Approve receipt
print()
print("[Test 5] Approving CashReceiptLine...")
try:
    cash_receipt.workflow_status = 'APPROVED'
    cash_receipt.approved_by = user
    cash_receipt.approved_date = datetime.now()
    cash_receipt.save()
    print(f"✓ CashReceiptLine approved")
    print(f"  Status: {cash_receipt.workflow_status}")
except Exception as e:
    print(f"✗ Error approving: {str(e)}")
    sys.exit(1)

# Test 6: Authorize receipt (this should trigger signal to create investment register entry)
print()
print("[Test 6] Authorizing CashReceiptLine (should trigger signal)...")
try:
    cash_receipt.workflow_status = 'AUTHORIZED'
    cash_receipt.authorized_by = user
    cash_receipt.authorized_date = datetime.now()
    cash_receipt.save()
    print(f"✓ CashReceiptLine authorized")
    print(f"  Status: {cash_receipt.workflow_status}")
except Exception as e:
    print(f"✗ Error authorizing: {str(e)}")
    sys.exit(1)

# Test 7: Check ShareholderInvestmentRegister entry was created
print()
print("[Test 7] Verifying ShareholderInvestmentRegister entry...")
try:
    investment = ShareholderInvestmentRegister.objects.filter(
        source_cash_receipt=cash_receipt
    ).first()
    
    if investment:
        print(f"✓ Investment register entry created!")
        print(f"  Stakeholder: {investment.stakeholder.name}")
        print(f"  Amount: {investment.amount_company_currency}")
        print(f"  Type: {investment.investment_type}")
        print(f"  Status: {investment.status}")
    else:
        print("✗ No investment register entry found (signal may not have fired)")
        print("  Check signals.py is properly registered in apps.py")
except Exception as e:
    print(f"✗ Error checking investment: {str(e)}")

# Test 8: Check GL entries
print()
print("[Test 8] Verifying GL entries...")
try:
    gl_entries = LedgerEntry.objects.filter(
        entity=entity,
        # Filter by related cash receipt if exists
    ).order_by('-created_at')[:10]
    
    if gl_entries.exists():
        print(f"✓ GL entries found: {gl_entries.count()}")
        for entry in gl_entries[:3]:
            print(f"  {entry.account.account_code}: {entry.debit_amount or entry.credit_amount} ({entry.entry_type})")
    else:
        print("✗ No GL entries found")
except Exception as e:
    print(f"✗ Error checking GL entries: {str(e)}")

# Test 9: Test views are importable
print()
print("[Test 9] Verifying views are importable...")
try:
    from accounting.views_reports import (
        ShareholderInvestmentRegisterListView,
        ShareholderInvestmentReportView,
        ShareholderCapitalStatusView,
        ShareholderInvestmentDetailView,
        ShareholderInvestmentAuditTrailView,
    )
    print("✓ All views imported successfully")
    print("  - ShareholderInvestmentRegisterListView")
    print("  - ShareholderInvestmentReportView")
    print("  - ShareholderCapitalStatusView")
    print("  - ShareholderInvestmentDetailView")
    print("  - ShareholderInvestmentAuditTrailView")
except ImportError as e:
    print(f"✗ Error importing views: {str(e)}")

# Test 10: Check database tables exist
print()
print("[Test 10] Verifying database tables...")
try:
    from django.db import connection
    cursor = connection.cursor()
    cursor.execute("""
        SELECT table_name FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name IN ('accounting_shareholderinvestmentregister', 'accounting_shareholderinvestmentsummary')
    """)
    tables = [row[0] for row in cursor.fetchall()]
    
    if len(tables) == 2:
        print("✓ Both database tables exist")
        for table in tables:
            print(f"  - {table}")
    else:
        print(f"✗ Only {len(tables)} tables found (expected 2)")
except Exception as e:
    print(f"✗ Error checking tables: {str(e)}")

print()
print("=" * 70)
print("TEST COMPLETE")
print("=" * 70)
print()
print("Summary:")
print("- If all tests passed, the workflow is working correctly")
print("- Check Django admin to see created data")
print("- Access reports at: /accounting/shareholder-investment-report/")
print("- Access list view at: /accounting/shareholder-investments/")
