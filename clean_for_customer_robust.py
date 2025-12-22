#!/usr/bin/env python
"""
Clean ERP data for customer delivery - Remove transactions but keep master data
"""

import os
import sys
sys.path.append('/var/www/tradifyerp')

import django
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from accounting.models import Account, LedgerEntry, Entity
from shareholder.models import CapitalContribution, Stakeholder

# Try to import financial report models
try:
    from accounting.models import TrialBalance
    trial_balance_available = True
except ImportError:
    trial_balance_available = False

try:
    from accounting.models import BalanceSheet  
    balance_sheet_available = True
except ImportError:
    balance_sheet_available = False

try:
    from accounting.models import ProfitLoss
    profit_loss_available = True
except ImportError:
    profit_loss_available = False

# Try to import cash management models
try:
    from cash_management.models import CashPosition, PaymentSchedule
    cash_mgmt_available = True
except ImportError:
    cash_mgmt_available = False

# Try to import cash models
try:
    from accounting.models import CashReceipt, CashPayment
    cash_models_available = True
except ImportError:
    cash_models_available = False

print("ERP DATA CLEANUP FOR CUSTOMER DELIVERY")
print("=" * 60)
print("This will remove all transaction data but keep:")
print("✅ Shareholders/Stakeholders")  
print("✅ Chart of Accounts structure")
print("✅ Entities")
print("✅ Currency setup")
print("✅ User accounts")
print()
print("Will remove:")
print("❌ All ledger entries")
print("❌ Capital contributions")
print("❌ Cash receipts & payments") 
print("❌ Financial reports")
print("❌ Cash management data")
print()

# Show current data counts
print("CURRENT DATA COUNTS:")
print("-" * 30)
print(f"Stakeholders: {Stakeholder.objects.count()}")
print(f"Entities: {Entity.objects.count()}")
print(f"Accounts: {Account.objects.count()}")
print(f"Ledger Entries: {LedgerEntry.objects.count()}")
print(f"Capital Contributions: {CapitalContribution.objects.count()}")

if trial_balance_available:
    print(f"Trial Balances: {TrialBalance.objects.count()}")
    
if balance_sheet_available:
    print(f"Balance Sheets: {BalanceSheet.objects.count()}")
    
if profit_loss_available:
    print(f"P&L Reports: {ProfitLoss.objects.count()}")

if cash_models_available:
    try:
        print(f"Cash Receipts: {CashReceipt.objects.count()}")
        print(f"Cash Payments: {CashPayment.objects.count()}")
    except:
        print("Cash Receipt/Payment counts not available")

if cash_mgmt_available:
    print(f"Cash Positions: {CashPosition.objects.count()}")
    print(f"Payment Schedules: {PaymentSchedule.objects.count()}")

print("\nSTARTING CLEANUP...")
print("=" * 30)

try:
    # 1. Clear Ledger Entries
    ledger_count = LedgerEntry.objects.count()
    if ledger_count > 0:
        LedgerEntry.objects.all().delete()
        print(f"✅ Deleted {ledger_count} ledger entries")
    
    # 2. Clear Capital Contributions
    capital_count = CapitalContribution.objects.count()
    if capital_count > 0:
        CapitalContribution.objects.all().delete()
        print(f"✅ Deleted {capital_count} capital contributions")
    
    # 3. Clear Financial Reports
    if trial_balance_available:
        tb_count = TrialBalance.objects.count()
        if tb_count > 0:
            TrialBalance.objects.all().delete()
            print(f"✅ Deleted {tb_count} trial balances")
    
    if balance_sheet_available:        
        bs_count = BalanceSheet.objects.count()
        if bs_count > 0:
            BalanceSheet.objects.all().delete()
            print(f"✅ Deleted {bs_count} balance sheets")
    
    if profit_loss_available:        
        pl_count = ProfitLoss.objects.count()
        if pl_count > 0:
            ProfitLoss.objects.all().delete()
            print(f"✅ Deleted {pl_count} P&L reports")
    
    # 4. Clear Cash Management Data
    if cash_mgmt_available:
        cash_pos_count = CashPosition.objects.count()
        payment_sched_count = PaymentSchedule.objects.count()
        
        if cash_pos_count > 0:
            CashPosition.objects.all().delete()
            print(f"✅ Deleted {cash_pos_count} cash positions")
            
        if payment_sched_count > 0:
            PaymentSchedule.objects.all().delete()
            print(f"✅ Deleted {payment_sched_count} payment schedules")
    
    # 5. Clear Cash Receipts & Payments (if available)
    if cash_models_available:
        try:
            cash_receipt_count = CashReceipt.objects.count()
            cash_payment_count = CashPayment.objects.count()
            
            if cash_receipt_count > 0:
                CashReceipt.objects.all().delete()
                print(f"✅ Deleted {cash_receipt_count} cash receipts")
                
            if cash_payment_count > 0:
                CashPayment.objects.all().delete()
                print(f"✅ Deleted {cash_payment_count} cash payments")
        except Exception as e:
            print(f"⚠️  Could not clear cash receipts/payments: {e}")
    
    # 6. Reset Account Opening Balances
    accounts_with_balances = Account.objects.exclude(opening_balance=0)
    reset_count = 0
    for account in accounts_with_balances:
        account.opening_balance = 0
        account.save()
        reset_count += 1
    
    if reset_count > 0:
        print(f"✅ Reset opening balances for {reset_count} accounts")
    
    # 7. Clear any other transaction tables using raw SQL
    from django.db import connection
    cursor = connection.cursor()
    
    # List of tables that might contain transaction data
    transaction_tables = [
        'accounting_journalentry',
        'accounting_journalentryline', 
        'cash_management_cashflow',
        'cash_management_banktransaction',
        'sales_salesorder',
        'sales_salesorderline',
        'purchase_purchaseorder',
        'purchase_purchaseorderline',
        'inventory_stockmovement',
        'inventory_stocktransaction'
    ]
    
    for table_name in transaction_tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            if count > 0:
                cursor.execute(f"DELETE FROM {table_name}")
                print(f"✅ Cleared {count} records from {table_name}")
        except Exception as e:
            # Table might not exist, skip
            pass
    
    print("\nCLEANUP COMPLETED SUCCESSFULLY!")
    print("=" * 40)
    
    # Show final counts
    print("FINAL DATA COUNTS:")
    print("-" * 20)
    print(f"Stakeholders: {Stakeholder.objects.count()} (PRESERVED)")
    print(f"Entities: {Entity.objects.count()} (PRESERVED)")
    print(f"Accounts: {Account.objects.count()} (PRESERVED)")
    print(f"Ledger Entries: {LedgerEntry.objects.count()}")
    print(f"Capital Contributions: {CapitalContribution.objects.count()}")
    
    if trial_balance_available:
        print(f"Trial Balances: {TrialBalance.objects.count()}")
    if cash_mgmt_available:
        print(f"Cash Positions: {CashPosition.objects.count()}")
    
    print("\n✅ PROJECT IS NOW CLEAN FOR CUSTOMER DELIVERY!")
    print("📋 Preserved Data:")
    print("   - All shareholders/stakeholders")
    print("   - Chart of accounts structure") 
    print("   - Entity setup")
    print("   - User accounts")
    print("   - Currency configuration")
    print("   - System configuration")
    
    print("\n🗑️  Removed Data:")
    print("   - All financial transactions")
    print("   - All ledger entries")
    print("   - All capital contributions")
    print("   - All cash receipts & payments")
    print("   - All financial reports")
    print("   - All sales/purchase orders")
    print("   - All inventory movements")
    
    print("\nCustomer can start fresh with clean system!")

except Exception as e:
    print(f"❌ ERROR during cleanup: {e}")
    import traceback
    traceback.print_exc()

print("\nCLEANUP COMPLETE!")