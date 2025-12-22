#!/usr/bin/env python3
"""
SAFE Transaction Data Cleaner
=============================
Interactive script with multiple confirmations for safety
"""

import os
import sys
import django
from datetime import datetime

# Setup Django environment
sys.path.append('/var/www/tradifyerp')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from django.db import transaction

def get_all_models_and_counts():
    """Get all models and their current counts"""
    try:
        from accounting.models import (
            LedgerEntry, TrialBalance, CashReceiptLine, 
            CashPaymentLine, BankReceiptLine, BankPaymentLine,
            JournalEntry, JournalEntryLine
        )
        from shareholder.models import CapitalContribution, InvestmentHistory
        from cash_management.models import CashPosition, CashTransaction
        
        models = [
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
        
        counts = []
        total_records = 0
        
        for name, model in models:
            try:
                count = model.objects.count()
                counts.append((name, count, model))
                total_records += count
            except Exception as e:
                counts.append((name, f"Error: {e}", None))
        
        return counts, total_records
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        return [], 0

def show_summary():
    """Show summary of what will be deleted"""
    print("=" * 70)
    print("🗂️  TRANSACTION DATA SUMMARY")
    print("=" * 70)
    
    counts, total = get_all_models_and_counts()
    
    for name, count, model in counts:
        if isinstance(count, int):
            print(f"{name:30}: {count:8,} records")
        else:
            print(f"{name:30}: {count}")
    
    print("-" * 70) 
    print(f"{'TOTAL RECORDS TO DELETE':30}: {total:8,}")
    print("=" * 70)
    
    return total > 0

def main():
    """Interactive main function"""
    print("🧹 TradifyERP Safe Transaction Data Cleaner")
    print(f"📅 {datetime.now().strftime('%B %d, %Y at %H:%M:%S')}")
    print()
    
    # Show what will be deleted
    has_data = show_summary()
    
    if not has_data:
        print("✅ No transaction data found to delete.")
        print("📝 Database appears to already be clean.")
        return
    
    print("\n⚠️  IMPORTANT SAFETY WARNINGS:")
    print("   • This will PERMANENTLY DELETE all transaction data")
    print("   • Master data (accounts, entities, users, currencies) will be preserved")
    print("   • This action CANNOT be undone")
    print("   • Make sure you have a database backup if needed")
    
    # Multiple confirmation steps
    print(f"\n❓ Step 1: Do you want to proceed with deletion?")
    step1 = input("   Type 'yes' to continue: ").lower().strip()
    if step1 != 'yes':
        print("❌ Operation cancelled at Step 1")
        return
    
    print(f"\n❓ Step 2: Are you sure this is for customer delivery?")
    step2 = input("   Type 'customer' to confirm: ").lower().strip()
    if step2 != 'customer':
        print("❌ Operation cancelled at Step 2") 
        return
        
    print(f"\n❓ Step 3: Final confirmation - Type 'DELETE' (in caps):")
    step3 = input("   Final confirmation: ").strip()
    if step3 != 'DELETE':
        print("❌ Operation cancelled at Step 3")
        return
    
    print(f"\n🚀 Starting deletion process...")
    
    try:
        # Import the main clearing function from the other script
        import subprocess
        result = subprocess.run([
            sys.executable, 
            '/var/www/tradifyerp/clear_transaction_data.py'
        ], capture_output=True, text=True, input='YES\n')
        
        if result.returncode == 0:
            print("✅ Transaction data cleared successfully!")
            print(result.stdout)
        else:
            print("❌ Error occurred during clearing:")
            print(result.stderr)
            
    except Exception as e:
        print(f"❌ Execution error: {e}")

if __name__ == "__main__":
    main()