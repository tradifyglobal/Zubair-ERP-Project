#!/usr/bin/env python3
"""Check shareholder entries for cash payment"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings_production')
django.setup()

from accounting.models import LedgerEntry, Account
from datetime import date

def main():
    # Find the specific cash payment entry
    print('=== LOOKING FOR CASH PAYMENT ENTRY ===')
    cash_entry = LedgerEntry.objects.filter(
        reference_number='CASH-PAYMENT-2',
        entry_type='CREDIT',
        amount='500.00'
    ).first()
    
    if cash_entry:
        print(f'✓ Found Cash Entry:')
        print(f'  ID: {cash_entry.id}')
        print(f'  Date: {cash_entry.entry_date}')
        print(f'  Account: {cash_entry.account.account_number} - {cash_entry.account.name}')
        print(f'  Type: {cash_entry.entry_type}')
        print(f'  Amount: {cash_entry.amount}')
        print(f'  Reference: {cash_entry.reference_number}')
        print(f'  Description: {cash_entry.description}')
        
        # Look for matching entries with same reference number
        print(f'\n=== LOOKING FOR MATCHING ENTRIES (Same Reference) ===')
        matching_entries = LedgerEntry.objects.filter(
            reference_number='CASH-PAYMENT-2'
        ).exclude(id=cash_entry.id)
        
        for entry in matching_entries:
            print(f'✓ Found Matching Entry:')
            print(f'  ID: {entry.id}')
            print(f'  Account: {entry.account.account_number} - {entry.account.name}')
            print(f'  Type: {entry.entry_type}')
            print(f'  Amount: {entry.amount}')
            print(f'  Account Type: {entry.account.account_type}')
            
            # Check if it's a shareholder/capital account
            if 'capital' in entry.account.name.lower() or entry.account.account_type == 'EQUITY':
                print(f'  🎯 SHAREHOLDER/CAPITAL ACCOUNT DETECTED!')
        
        if not matching_entries.exists():
            print('  ❌ No matching entries found with same reference number')
            
        # Look for entries on same date with similar amount
        print(f'\n=== LOOKING FOR ENTRIES ON SAME DATE (Dec 16, 2025) ===')
        same_date_entries = LedgerEntry.objects.filter(
            entry_date=date(2025, 12, 16),
            amount='500.00'
        ).exclude(id=cash_entry.id)
        
        for entry in same_date_entries:
            print(f'• Entry ID {entry.id}: {entry.account.account_number} - {entry.account.name}')
            print(f'  Type: {entry.entry_type}, Amount: {entry.amount}')
            print(f'  Reference: {entry.reference_number}')
            
            if 'capital' in entry.account.name.lower() or entry.account.account_type == 'EQUITY':
                print(f'  🎯 SHAREHOLDER/CAPITAL ACCOUNT!')
        
        # Look for capital contributions around this time
        print(f'\n=== CHECKING CAPITAL CONTRIBUTIONS ===')
        try:
            from accounting.models import CapitalContribution
            contributions = CapitalContribution.objects.filter(
                contribution_date=date(2025, 12, 16),
                amount_company_currency='500.00'
            )
            
            for contrib in contributions:
                print(f'✓ Found Capital Contribution:')
                print(f'  ID: {contrib.id}')
                print(f'  Stakeholder: {contrib.stakeholder.full_name}')
                print(f'  Amount: {contrib.amount_company_currency}')
                print(f'  Status: {contrib.status}')
        except ImportError:
            print('  Capital Contribution model not available')
        
        # Check all equity accounts for recent activity
        print(f'\n=== CHECKING ALL EQUITY ACCOUNTS ===')
        equity_accounts = Account.objects.filter(
            entity=cash_entry.entity,
            account_type='EQUITY'
        )
        
        for acc in equity_accounts:
            recent_entries = acc.ledger_entries.filter(
                entry_date=date(2025, 12, 16),
                amount='500.00'
            )
            if recent_entries.exists():
                for entry in recent_entries:
                    print(f'• {acc.account_number} - {acc.name}:')
                    print(f'  Entry ID: {entry.id}, Type: {entry.entry_type}')
                    print(f'  Reference: {entry.reference_number}')
    else:
        print('❌ Cash payment entry not found')
        
        # Let's search more broadly
        print('\n=== SEARCHING BROADLY FOR SIMILAR ENTRIES ===')
        similar_entries = LedgerEntry.objects.filter(
            entry_date=date(2025, 12, 16),
            amount='500.00'
        )
        
        for entry in similar_entries:
            print(f'• Entry ID {entry.id}: {entry.account.account_number} - {entry.account.name}')
            print(f'  Type: {entry.entry_type}, Reference: {entry.reference_number}')

if __name__ == '__main__':
    main()