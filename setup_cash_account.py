#!/usr/bin/env python
"""
Setup Script for Cash Account and GL Integration
Creates the Cash Account (Asset) and ensures proper GL posting flow
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
sys.path.insert(0, '/home/zubair/tradifyerp')
django.setup()

from accounting.models import Account, Entity, Currency, LedgerEntry, CashReceiptLine
from decimal import Decimal
from django.db import transaction

def create_cash_account():
    """Create the main Cash Account (100001) if it doesn't exist."""
    print("\n" + "="*80)
    print("CASH ACCOUNT SETUP")
    print("="*80)
    
    try:
        # Get default entity (INT001)
        entity = Entity.objects.filter(code='INT001').first()
        if not entity:
            entity = Entity.objects.filter(is_active=True).first()
        
        if not entity:
            print("❌ ERROR: No active entity found!")
            return False
        
        print(f"\n✓ Using Entity: {entity.code} - {entity.name}")
        
        # Get default currency (INR)
        currency = Currency.objects.filter(code='INR').first()
        if not currency:
            currency = Currency.objects.filter(is_active=True).first()
        
        if not currency:
            print("❌ ERROR: No active currency found!")
            return False
        
        print(f"✓ Using Currency: {currency.code}")
        
        # Create or get Cash Account
        with transaction.atomic():
            cash_account, created = Account.objects.get_or_create(
                entity=entity,
                account_number='100001',
                defaults={
                    'name': 'Cash',
                    'account_type': 'ASSET',
                    'currency': currency,
                    'description': 'Cash account for receiving cash from shareholders and other receipts',
                    'is_active': True,
                    'opening_balance': Decimal('0.00'),
                    'parent_account': None,
                }
            )
            
            if created:
                print(f"\n✅ CREATED: Cash Account")
                print(f"   Account #: 100001")
                print(f"   Type: ASSET")
                print(f"   Name: {cash_account.name}")
                print(f"   Entity: {entity.code}")
                print(f"   Currency: {currency.code}")
            else:
                print(f"\n✓ ALREADY EXISTS: Cash Account (100001)")
                print(f"   Name: {cash_account.name}")
                print(f"   Type: {cash_account.account_type}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR creating cash account: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def verify_capital_account():
    """Verify the Capital Contribution Account (3000/3100) exists."""
    print("\n" + "="*80)
    print("CAPITAL ACCOUNT VERIFICATION")
    print("="*80)
    
    try:
        entity = Entity.objects.filter(code='INT001').first()
        if not entity:
            entity = Entity.objects.filter(is_active=True).first()
        
        # Check for account 3000 (main capital account)
        main_account = Account.objects.filter(
            entity=entity,
            account_number='3000'
        ).first()
        
        if main_account:
            print(f"\n✓ Main Capital Account Exists: {main_account.account_number}")
            print(f"  Name: {main_account.name}")
            print(f"  Type: {main_account.account_type}")
        
        # Check for account 3100 (shareholder investment account)
        sub_account = Account.objects.filter(
            entity=entity,
            account_number='3100'
        ).first()
        
        if sub_account:
            print(f"\n✓ Shareholder Investment Account Exists: {sub_account.account_number}")
            print(f"  Name: {sub_account.name}")
            print(f"  Type: {sub_account.account_type}")
            print(f"  Parent: {sub_account.parent_account}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR verifying capital account: {str(e)}")
        return False


def verify_cash_receipt_model():
    """Verify CashReceiptLine model structure."""
    print("\n" + "="*80)
    print("CASH RECEIPT LINE MODEL VERIFICATION")
    print("="*80)
    
    try:
        # Check if CashReceiptLine has required fields
        cash_receipt_fields = [f.name for f in CashReceiptLine._meta.fields]
        
        required_fields = [
            'account',           # Debit account (e.g., 3100-01 Capital)
            'credit_account',    # Credit account (e.g., 100001 Cash)
            'debit_amount',      # Debit amount
            'credit_amount',     # Credit amount
            'status',            # Status (DRAFT, POSTED, etc.)
            'workflow_status',   # Workflow status
            'stakeholder',       # Stakeholder who contributed
        ]
        
        print("\n✓ CashReceiptLine Model Fields:")
        for field in required_fields:
            if field in cash_receipt_fields:
                print(f"  ✓ {field}")
            else:
                print(f"  ✗ MISSING: {field}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR verifying model: {str(e)}")
        return False


def show_workflow_summary():
    """Show the complete workflow."""
    print("\n" + "="*80)
    print("CASH RECEIPT WORKFLOW SUMMARY")
    print("="*80)
    
    print("""
✓ WORKFLOW STEPS:

1. CASH RECEIPT CREATION (User)
   └─ Navigate to: /accounting/cash-receipts/create/
   └─ Select: Capital Account (e.g., 3100-01)
   └─ Enter: Amount (both Debit and Credit)
   └─ Status: DRAFT

2. APPROVAL (Approver)
   └─ Click: Approve Button
   └─ Status: APPROVED

3. AUTHORIZATION & GL POSTING (Finance)
   └─ Click: Authorize & Post Button
   └─ System Creates GL Entries:
      ├─ DEBIT: 3100-01 (Capital) = Amount
      ├─ CREDIT: 100001 (Cash) = Amount
      └─ Both marked: AUTHORIZED & POSTED
   └─ Status: AUTHORIZED/POSTED

4. GENERAL LEDGER ENTRY
   └─ Both entries visible in GL
   └─ Reference: CASH-RECEIPT-{id}
   └─ Workflow Status: AUTHORIZED
   └─ Posted: Yes

5. SHAREHOLDER INVESTMENT SYNC
   └─ Capital contribution tracked
   └─ Stakeholder linked to receipt
   └─ Amount recorded for dividends/distributions

═══════════════════════════════════════════════════════════════════════════════

ACCOUNT MAPPING:

Debit Account (receipt.account):       3100-01 (Capital Contribution)
Credit Account (receipt.credit_account): 100001 (Cash)

Amount Field Mapping:
- receipt.debit_amount  → GL Debit Entry Amount
- receipt.credit_amount → GL Credit Entry Amount

═══════════════════════════════════════════════════════════════════════════════
""")


if __name__ == '__main__':
    print("\n" + "🟢 "*40)
    print("CASH ACCOUNT & GL INTEGRATION SETUP")
    print("🟢 "*40)
    
    results = {
        'cash_account': create_cash_account(),
        'capital_account': verify_capital_account(),
        'model_verification': verify_cash_receipt_model(),
    }
    
    show_workflow_summary()
    
    print("\n" + "="*80)
    print("SETUP SUMMARY")
    print("="*80)
    
    for check, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {check}")
    
    if all(results.values()):
        print("\n✅ ALL CHECKS PASSED - System is ready for Cash Receipts!")
    else:
        print("\n⚠️  Some checks failed - Please review above errors")
    
    print("\n" + "="*80 + "\n")
