#!/usr/bin/env python3
"""
Clear Transaction Data Script - Updated
=====================================
This script clears all transaction data while preserving master data setup.
Run this before giving database to customer for a clean start.
"""

import os
import sys
import django
from django.db import transaction, connection

# Setup Django environment
sys.path.append('/var/www/tradifyerp')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

# Import all the models we need to clear (using actual available models)
from accounting.models import (
    LedgerEntry, 
    TrialBalance, 
    CashReceiptLine, 
    CashPaymentLine, 
    BankReceiptLine, 
    BankPaymentLine,
    AuditLog,
    ReconciliationEntry,
    ReconciliationMatch,
    ReconciliationRecord,
    CashTransaction,
    VendorPayment,
    TaxTransaction,
    TaxSummary,
    BalanceSheet,
    ProfitLossReport
)
from shareholder.models import (
    CapitalContribution,
)
from cash_management.models import (
    CashPosition,
    PaymentSchedule,
    LiquidityForecast,
    LiquidityForecastLine,
    FXExposure
)

def print_counts_before():
    """Print record counts before deletion"""
    print("=" * 70)
    print("RECORD COUNTS BEFORE DELETION")
    print("=" * 70)
    
    models_to_check = [
        ("Cash Receipt Lines", CashReceiptLine),
        ("Cash Payment Lines", CashPaymentLine), 
        ("Bank Receipt Lines", BankReceiptLine),
        ("Bank Payment Lines", BankPaymentLine),
        ("Ledger Entries", LedgerEntry),
        ("Trial Balances", TrialBalance),
        ("Capital Contributions", CapitalContribution),
        ("Audit Logs", AuditLog),
        ("Reconciliation Entries", ReconciliationEntry),
        ("Reconciliation Matches", ReconciliationMatch),
        ("Reconciliation Records", ReconciliationRecord),
        ("Cash Transactions", CashTransaction),
        ("Vendor Payments", VendorPayment),
        ("Tax Transactions", TaxTransaction),
        ("Tax Summary", TaxSummary),
        ("Balance Sheets", BalanceSheet),
        ("Profit Loss Reports", ProfitLossReport),
        ("Cash Positions", CashPosition),
        ("Payment Schedules", PaymentSchedule),
        ("Liquidity Forecasts", LiquidityForecast),
        ("Liquidity Forecast Lines", LiquidityForecastLine),
        ("FX Exposures", FXExposure),
    ]
    
    total_records = 0
    for name, model in models_to_check:
        try:
            count = model.objects.count()
            print(f"{name:30}: {count:8,} records")
            total_records += count
        except Exception as e:
            print(f"{name:30}: Error - {e}")
    
    print("-" * 70)
    print(f"{'TOTAL RECORDS':30}: {total_records:8,}")
    print("=" * 70)
    return total_records

def clear_transaction_data():
    """Clear all transaction data in the correct order"""
    print("\n🧹 Starting transaction data cleanup...")
    
    deletion_summary = {}
    
    with transaction.atomic():
        try:
            # 1. Clear dependent records first (in reverse FK order)
            
            # Clear reconciliation data
            print("🔄 Clearing Reconciliation Records...")
            deleted = ReconciliationMatch.objects.all().delete()
            deletion_summary["Reconciliation Matches"] = deleted[0]
            print(f"   ✅ Deleted {deleted[0]} reconciliation matches")
            
            deleted = ReconciliationEntry.objects.all().delete()
            deletion_summary["Reconciliation Entries"] = deleted[0]
            print(f"   ✅ Deleted {deleted[0]} reconciliation entries")
            
            deleted = ReconciliationRecord.objects.all().delete()
            deletion_summary["Reconciliation Records"] = deleted[0]
            print(f"   ✅ Deleted {deleted[0]} reconciliation records")
            
            # Clear forecasting data
            print("📊 Clearing Forecasting Data...")
            deleted = LiquidityForecastLine.objects.all().delete()
            deletion_summary["Liquidity Forecast Lines"] = deleted[0]
            print(f"   ✅ Deleted {deleted[0]} liquidity forecast lines")
            
            deleted = LiquidityForecast.objects.all().delete()
            deletion_summary["Liquidity Forecasts"] = deleted[0]
            print(f"   ✅ Deleted {deleted[0]} liquidity forecasts")
            
            deleted = FXExposure.objects.all().delete()
            deletion_summary["FX Exposures"] = deleted[0]
            print(f"   ✅ Deleted {deleted[0]} FX exposures")
            
            # Clear reports (they may reference other data)
            print("📈 Clearing Reports...")
            deleted = BalanceSheet.objects.all().delete()
            deletion_summary["Balance Sheets"] = deleted[0]
            print(f"   ✅ Deleted {deleted[0]} balance sheets")
            
            deleted = ProfitLossReport.objects.all().delete()
            deletion_summary["Profit Loss Reports"] = deleted[0]
            print(f"   ✅ Deleted {deleted[0]} profit/loss reports")
            
            # Clear tax data
            print("💰 Clearing Tax Data...")
            deleted = TaxSummary.objects.all().delete()
            deletion_summary["Tax Summary"] = deleted[0]
            print(f"   ✅ Deleted {deleted[0]} tax summary records")
            
            deleted = TaxTransaction.objects.all().delete()
            deletion_summary["Tax Transactions"] = deleted[0]
            print(f"   ✅ Deleted {deleted[0]} tax transactions")
            
            # Clear vendor payments
            print("🏪 Clearing Vendor Payments...")
            deleted = VendorPayment.objects.all().delete()
            deletion_summary["Vendor Payments"] = deleted[0]
            print(f"   ✅ Deleted {deleted[0]} vendor payments")
            
            # Clear cash management
            print("💰 Clearing Cash Management...")
            deleted = PaymentSchedule.objects.all().delete()
            deletion_summary["Payment Schedules"] = deleted[0]
            print(f"   ✅ Deleted {deleted[0]} payment schedules")
            
            deleted = CashPosition.objects.all().delete()
            deletion_summary["Cash Positions"] = deleted[0]
            print(f"   ✅ Deleted {deleted[0]} cash positions")
            
            # Clear cash transactions from accounting
            print("🏦 Clearing Cash Transactions...")
            deleted = CashTransaction.objects.all().delete()
            deletion_summary["Cash Transactions"] = deleted[0]
            print(f"   ✅ Deleted {deleted[0]} cash transactions")
            
            # Clear transaction lines
            print("🧾 Clearing Transaction Lines...")
            deleted = CashReceiptLine.objects.all().delete()
            deletion_summary["Cash Receipt Lines"] = deleted[0]
            print(f"   ✅ Deleted {deleted[0]} cash receipt lines")
            
            deleted = CashPaymentLine.objects.all().delete()
            deletion_summary["Cash Payment Lines"] = deleted[0]
            print(f"   ✅ Deleted {deleted[0]} cash payment lines")
            
            deleted = BankReceiptLine.objects.all().delete()
            deletion_summary["Bank Receipt Lines"] = deleted[0]
            print(f"   ✅ Deleted {deleted[0]} bank receipt lines")
            
            deleted = BankPaymentLine.objects.all().delete()
            deletion_summary["Bank Payment Lines"] = deleted[0]
            print(f"   ✅ Deleted {deleted[0]} bank payment lines")
            
            # Clear shareholder data
            print("📈 Clearing Shareholder Data...")
            deleted = CapitalContribution.objects.all().delete()
            deletion_summary["Capital Contributions"] = deleted[0]
            print(f"   ✅ Deleted {deleted[0]} capital contributions")
            
            # Clear trial balances
            print("⚖️  Clearing Trial Balances...")
            deleted = TrialBalance.objects.all().delete()
            deletion_summary["Trial Balances"] = deleted[0]
            print(f"   ✅ Deleted {deleted[0]} trial balances")
            
            # Clear audit logs (optional - you might want to keep these)
            print("📋 Clearing Audit Logs...")
            confirm_audit = input("   Clear audit logs too? (y/N): ").lower().strip()
            if confirm_audit == 'y':
                deleted = AuditLog.objects.all().delete()
                deletion_summary["Audit Logs"] = deleted[0]
                print(f"   ✅ Deleted {deleted[0]} audit logs")
            else:
                deletion_summary["Audit Logs"] = "Skipped"
                print("   ⏭️  Skipped audit logs")
            
            # Clear ledger entries (last, as other records may reference them)
            print("📚 Clearing Ledger Entries...")
            deleted = LedgerEntry.objects.all().delete()
            deletion_summary["Ledger Entries"] = deleted[0]
            print(f"   ✅ Deleted {deleted[0]} ledger entries")
            
            print("\n🎉 Transaction data cleanup completed successfully!")
            return deletion_summary
            
        except Exception as e:
            print(f"\n❌ Error during cleanup: {e}")
            raise e

def reset_auto_increment_sequences():
    """Reset auto-increment sequences to start from 1"""
    print("\n🔄 Resetting auto-increment sequences...")
    
    tables_to_reset = [
        'accounting_ledgerentry',
        'accounting_trialbalance', 
        'accounting_cashreceiptline',
        'accounting_cashpaymentline',
        'accounting_bankreceiptline',
        'accounting_bankpaymentline',
        'accounting_auditlog',
        'accounting_reconciliationentry',
        'accounting_reconciliationmatch', 
        'accounting_reconciliationrecord',
        'accounting_cashtransaction',
        'accounting_vendorpayment',
        'accounting_taxtransaction',
        'accounting_taxsummary',
        'accounting_balancesheet',
        'accounting_profitlossreport',
        'shareholder_capitalcontribution',
        'cash_management_cashposition',
        'cash_management_paymentschedule',
        'cash_management_liquidityforecast',
        'cash_management_liquidityforecastline',
        'cash_management_fxexposure',
    ]
    
    with connection.cursor() as cursor:
        for table in tables_to_reset:
            try:
                # Reset PostgreSQL sequence
                cursor.execute(f"SELECT setval(pg_get_serial_sequence('{table}', 'id'), 1, false);")
                print(f"   ✅ Reset sequence for {table}")
            except Exception as e:
                print(f"   ⚠️  Could not reset sequence for {table}: {e}")

def print_counts_after():
    """Print record counts after deletion"""
    print("\n" + "=" * 70)
    print("RECORD COUNTS AFTER DELETION")
    print("=" * 70)
    
    models_to_check = [
        ("Cash Receipt Lines", CashReceiptLine),
        ("Cash Payment Lines", CashPaymentLine), 
        ("Bank Receipt Lines", BankReceiptLine),
        ("Bank Payment Lines", BankPaymentLine),
        ("Ledger Entries", LedgerEntry),
        ("Trial Balances", TrialBalance),
        ("Capital Contributions", CapitalContribution),
        ("Audit Logs", AuditLog),
        ("Cash Transactions", CashTransaction),
        ("Vendor Payments", VendorPayment),
        ("Cash Positions", CashPosition),
    ]
    
    total_remaining = 0
    for name, model in models_to_check:
        try:
            count = model.objects.count()
            print(f"{name:30}: {count:8,} records")
            total_remaining += count
        except Exception as e:
            print(f"{name:30}: Error - {e}")
    
    print("-" * 70)
    print(f"{'TOTAL REMAINING':30}: {total_remaining:8,}")
    print("=" * 70)
    return total_remaining

def main():
    """Main execution function"""
    print("🚀 TradifyERP Transaction Data Cleanup (Updated)")
    print("📅 Date: December 16, 2025")
    print("⚠️  WARNING: This will permanently delete all transaction data!")
    print("✅ Master data (accounts, entities, currencies, users) will be preserved")
    print()
    
    # Show before counts
    total_before = print_counts_before()
    
    if total_before == 0:
        print("\n✅ No transaction data found to delete.")
        print("📝 Database appears to already be clean.")
        return
    
    # Confirm before proceeding
    print("\n🤔 Are you sure you want to proceed?")
    print("   This action cannot be undone!")
    
    confirm = input("Type 'YES' to confirm: ")
    if confirm != 'YES':
        print("❌ Operation cancelled")
        return
    
    try:
        # Clear all transaction data
        summary = clear_transaction_data()
        
        # Reset sequences
        reset_auto_increment_sequences()
        
        # Show after counts  
        total_after = print_counts_after()
        
        print("\n" + "=" * 70)
        print("✅ DATABASE CLEANUP COMPLETED SUCCESSFULLY")
        print("=" * 70)
        print("🎯 The database is now clean and ready for customer delivery")
        print("📋 All master data (accounts, entities, currencies) has been preserved")
        print("🔢 Auto-increment sequences have been reset to start from 1")
        print(f"📊 Deleted {total_before} records, {total_after} remain")
        print("🚀 You can now create fresh transactions with clean ID sequences")
        
        # Show deletion summary
        print("\n📋 DELETION SUMMARY:")
        for category, count in summary.items():
            print(f"   {category:25}: {count}")
        
    except Exception as e:
        print(f"\n❌ CLEANUP FAILED: {e}")
        print("💾 Database has been rolled back to previous state")
        sys.exit(1)

if __name__ == "__main__":
    main()