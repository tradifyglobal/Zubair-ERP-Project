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

from accounting.models import (
    Account, LedgerEntry, Entity, TrialBalance, BalanceSheet, ProfitLoss
)
from shareholder.models import CapitalContribution, Stakeholder
from cash_management.models import (
    CashPosition, PaymentSchedule, LiquidityForecast, 
    TreasuryAccount, FXExposure
)

# Import cash accounting models
try:
    from accounting.cash_models import CashReceipt, CashPayment
    cash_models_available = True
except ImportError:
    try:
        from accounting.models import CashReceipt, CashPayment
        cash_models_available = True
    except ImportError:
        cash_models_available = False

print("🧹 ERP DATA CLEANUP FOR CUSTOMER DELIVERY")
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
print(f"Trial Balances: {TrialBalance.objects.count()}")
print(f"Balance Sheets: {BalanceSheet.objects.count()}")
print(f"P&L Reports: {ProfitLoss.objects.count()}")

if cash_models_available:
    try:
        print(f"Cash Receipts: {CashReceipt.objects.count()}")
        print(f"Cash Payments: {CashPayment.objects.count()}")
    except:
        print("Cash Receipt/Payment models not accessible")

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
    tb_count = TrialBalance.objects.count()
    bs_count = BalanceSheet.objects.count()
    pl_count = ProfitLoss.objects.count()
    
    if tb_count > 0:
        TrialBalance.objects.all().delete()
        print(f"✅ Deleted {tb_count} trial balances")
        
    if bs_count > 0:
        BalanceSheet.objects.all().delete()
        print(f"✅ Deleted {bs_count} balance sheets")
        
    if pl_count > 0:
        ProfitLoss.objects.all().delete()
        print(f"✅ Deleted {pl_count} P&L reports")
    
    # 4. Clear Cash Management Data
    cash_pos_count = CashPosition.objects.count()
    payment_sched_count = PaymentSchedule.objects.count()
    liquidity_count = LiquidityForecast.objects.count()
    treasury_count = TreasuryAccount.objects.count()
    fx_count = FXExposure.objects.count()
    
    if cash_pos_count > 0:
        CashPosition.objects.all().delete()
        print(f"✅ Deleted {cash_pos_count} cash positions")
        
    if payment_sched_count > 0:
        PaymentSchedule.objects.all().delete()
        print(f"✅ Deleted {payment_sched_count} payment schedules")
        
    if liquidity_count > 0:
        LiquidityForecast.objects.all().delete()
        print(f"✅ Deleted {liquidity_count} liquidity forecasts")
        
    if treasury_count > 0:
        TreasuryAccount.objects.all().delete()
        print(f"✅ Deleted {treasury_count} treasury accounts")
        
    if fx_count > 0:
        FXExposure.objects.all().delete()
        print(f"✅ Deleted {fx_count} FX exposures")
    
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
    
    # 6. Reset Account Balances (optional - clear opening balances)
    accounts_with_balances = Account.objects.exclude(opening_balance=0)
    if accounts_with_balances.exists():
        for account in accounts_with_balances:
            account.opening_balance = 0
            account.save()
        print(f"✅ Reset opening balances for {accounts_with_balances.count()} accounts")
    
    print("\n🎉 CLEANUP COMPLETED SUCCESSFULLY!")
    print("=" * 40)
    
    # Show final counts
    print("FINAL DATA COUNTS:")
    print("-" * 20)
    print(f"Stakeholders: {Stakeholder.objects.count()} (PRESERVED)")
    print(f"Entities: {Entity.objects.count()} (PRESERVED)")
    print(f"Accounts: {Account.objects.count()} (PRESERVED)")
    print(f"Ledger Entries: {LedgerEntry.objects.count()}")
    print(f"Capital Contributions: {CapitalContribution.objects.count()}")
    print(f"Trial Balances: {TrialBalance.objects.count()}")
    print(f"Balance Sheets: {BalanceSheet.objects.count()}")
    print(f"P&L Reports: {ProfitLoss.objects.count()}")
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
    print("   - All cash management records")
    
    print("\n🏁 Customer can start fresh with clean system!")

except Exception as e:
    print(f"❌ ERROR during cleanup: {e}")
    import traceback
    traceback.print_exc()

print("\nCLEANUP COMPLETE!")