#!/usr/bin/env python3
"""
Clear Transaction Data Script
============================
This script clears all transaction data while preserving master data setup.
Run this before giving database to customer for a clean start.
"""

import os
import sys
import django
from django.db import transaction, connection
from django.core.management import setup_environ

# Setup Django environment
sys.path.append('/var/www/tradifyerp')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

# Import all the models we need to clear
from accounting.models import (
    LedgerEntry, 
    TrialBalance, 
    CashReceiptLine, 
    CashPaymentLine, 
    BankReceiptLine, 
    BankPaymentLine,
    JournalEntry,
    JournalEntryLine
)
from shareholder.models import (
    CapitalContribution, 
    InvestmentHistory,
    ShareholderInvestment
)
from cash_management.models import (
    CashPosition,
    CashTransaction
)

def print_counts_before():
    """Print record counts before deletion"""
    print("=" * 60)
    print("RECORD COUNTS BEFORE DELETION")
    print("=" * 60)
    
    models_to_check = [
        ("Cash Receipt Lines", CashReceiptLine),
        ("Cash Payment Lines", CashPaymentLine), 
        ("Bank Receipt Lines", BankReceiptLine),
        ("Bank Payment Lines", BankPaymentLine),
        ("Ledger Entries", LedgerEntry),
        ("Trial Balances", TrialBalance),
        ("Capital Contributions", CapitalContribution),
        ("Investment History", InvestmentHistory),
        ("Journal Entries", JournalEntry),
        ("Journal Entry Lines", JournalEntryLine),
        ("Cash Positions", CashPosition),
        ("Cash Transactions", CashTransaction),
    ]
    
    for name, model in models_to_check:
        try:
            count = model.objects.count()
            print(f"{name:25}: {count:6,} records")
        except Exception as e:
            print(f"{name:25}: Error - {e}")
    print()

def clear_transaction_data():
    """Clear all transaction data in the correct order"""
    print("🧹 Starting transaction data cleanup...")
    
    with transaction.atomic():
        try:
            # 1. Clear dependent records first (in reverse FK order)
            print("📋 Clearing Journal Entry Lines...")
            deleted_journal_lines = JournalEntryLine.objects.all().delete()
            print(f"   ✅ Deleted {deleted_journal_lines[0]} journal entry lines")
            
            print("📋 Clearing Journal Entries...")  
            deleted_journals = JournalEntry.objects.all().delete()
            print(f"   ✅ Deleted {deleted_journals[0]} journal entries")
            
            # 2. Clear Cash Management data
            print("💰 Clearing Cash Transactions...")
            deleted_cash_trans = CashTransaction.objects.all().delete()
            print(f"   ✅ Deleted {deleted_cash_trans[0]} cash transactions")
            
            print("💰 Clearing Cash Positions...")
            deleted_cash_pos = CashPosition.objects.all().delete() 
            print(f"   ✅ Deleted {deleted_cash_pos[0]} cash positions")
            
            # 3. Clear Cash Receipt/Payment Lines
            print("🧾 Clearing Cash Receipt Lines...")
            deleted_receipt_lines = CashReceiptLine.objects.all().delete()
            print(f"   ✅ Deleted {deleted_receipt_lines[0]} cash receipt lines")
            
            print("🧾 Clearing Cash Payment Lines...")
            deleted_payment_lines = CashPaymentLine.objects.all().delete()
            print(f"   ✅ Deleted {deleted_payment_lines[0]} cash payment lines")
            
            # 4. Clear Bank Receipt/Payment Lines  
            print("🏦 Clearing Bank Receipt Lines...")
            deleted_bank_receipts = BankReceiptLine.objects.all().delete()
            print(f"   ✅ Deleted {deleted_bank_receipts[0]} bank receipt lines")
            
            print("🏦 Clearing Bank Payment Lines...")
            deleted_bank_payments = BankPaymentLine.objects.all().delete()
            print(f"   ✅ Deleted {deleted_bank_payments[0]} bank payment lines")
            
            # 5. Clear Shareholder Investment data
            print("📈 Clearing Investment History...")
            deleted_investment_history = InvestmentHistory.objects.all().delete()
            print(f"   ✅ Deleted {deleted_investment_history[0]} investment history records")
            
            print("📈 Clearing Shareholder Investments...")
            try:
                deleted_shareholder_investments = ShareholderInvestment.objects.all().delete()
                print(f"   ✅ Deleted {deleted_shareholder_investments[0]} shareholder investments")
            except Exception as e:
                print(f"   ⚠️  ShareholderInvestment model not found or error: {e}")
            
            # 6. Clear Capital Contributions
            print("💵 Clearing Capital Contributions...")
            deleted_contributions = CapitalContribution.objects.all().delete()
            print(f"   ✅ Deleted {deleted_contributions[0]} capital contributions")
            
            # 7. Clear Trial Balances
            print("⚖️  Clearing Trial Balances...")
            deleted_trial_balances = TrialBalance.objects.all().delete()
            print(f"   ✅ Deleted {deleted_trial_balances[0]} trial balances")
            
            # 8. Clear Ledger Entries (last, as other records may reference them)
            print("📚 Clearing Ledger Entries...")
            deleted_ledger_entries = LedgerEntry.objects.all().delete()
            print(f"   ✅ Deleted {deleted_ledger_entries[0]} ledger entries")
            
            print("\n🎉 Transaction data cleanup completed successfully!")
            
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
        'accounting_journalentry',
        'accounting_journalentryline',
        'shareholder_capitalcontribution',
        'shareholder_investmenthistory',
        'cash_management_cashposition',
        'cash_management_cashtransaction',
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
    print("\n" + "=" * 60)
    print("RECORD COUNTS AFTER DELETION")
    print("=" * 60)
    
    models_to_check = [
        ("Cash Receipt Lines", CashReceiptLine),
        ("Cash Payment Lines", CashPaymentLine), 
        ("Bank Receipt Lines", BankReceiptLine),
        ("Bank Payment Lines", BankPaymentLine),
        ("Ledger Entries", LedgerEntry),
        ("Trial Balances", TrialBalance),
        ("Capital Contributions", CapitalContribution),
        ("Investment History", InvestmentHistory),
        ("Journal Entries", JournalEntry),
        ("Journal Entry Lines", JournalEntryLine),
        ("Cash Positions", CashPosition),
        ("Cash Transactions", CashTransaction),
    ]
    
    for name, model in models_to_check:
        try:
            count = model.objects.count()
            print(f"{name:25}: {count:6,} records")
        except Exception as e:
            print(f"{name:25}: Error - {e}")

def main():
    """Main execution function"""
    print("🚀 TradifyERP Transaction Data Cleanup")
    print("📅 Date: December 16, 2025")
    print("⚠️  WARNING: This will permanently delete all transaction data!")
    print("✅ Master data (accounts, entities, currencies, users) will be preserved")
    
    # Show before counts
    print_counts_before()
    
    # Confirm before proceeding
    print("🤔 Are you sure you want to proceed?")
    print("   This action cannot be undone!")
    
    # For automated execution, comment out the input line below
    confirm = input("Type 'YES' to confirm: ")
    if confirm != 'YES':
        print("❌ Operation cancelled")
        return
    
    try:
        # Clear all transaction data
        clear_transaction_data()
        
        # Reset sequences
        reset_auto_increment_sequences()
        
        # Show after counts  
        print_counts_after()
        
        print("\n" + "=" * 60)
        print("✅ DATABASE CLEANUP COMPLETED SUCCESSFULLY")
        print("=" * 60)
        print("🎯 The database is now clean and ready for customer delivery")
        print("📋 All master data (accounts, entities, currencies) has been preserved")
        print("🔢 Auto-increment sequences have been reset to start from 1")
        print("🚀 You can now create fresh transactions with clean ID sequences")
        
    except Exception as e:
        print(f"\n❌ CLEANUP FAILED: {e}")
        print("💾 Database has been rolled back to previous state")
        sys.exit(1)

if __name__ == "__main__":
    main()