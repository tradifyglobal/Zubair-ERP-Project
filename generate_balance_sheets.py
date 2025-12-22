#!/usr/bin/env python3

import os
import sys
import django

sys.path.append('/var/www/tradifyerp')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from accounting.models import Entity, BalanceSheet, LedgerEntry, Account
from decimal import Decimal
from datetime import date

def check_balance_sheet_data():
    print("=== BALANCE SHEET DATA ANALYSIS ===")
    
    entities = Entity.objects.all()
    
    for entity in entities:
        print(f"\nEntity: {entity.name} (ID: {entity.id})")
        
        # Check existing balance sheet records
        bs_records = BalanceSheet.objects.filter(entity=entity)
        print(f"  Existing balance sheet records: {bs_records.count()}")
        
        for bs in bs_records:
            print(f"    {bs.as_of_date}: Assets {bs.total_assets} | Liabilities {bs.total_liabilities} | Equity {bs.total_equity}")
        
        # Check ledger entries for balance sheet accounts
        ledger_entries = LedgerEntry.objects.filter(entity=entity)
        print(f"  Ledger entries: {ledger_entries.count()}")
        
        if ledger_entries.count() > 0:
            # Categorize accounts by type
            asset_accounts = []
            liability_accounts = []
            equity_accounts = []
            
            for entry in ledger_entries:
                account_type = entry.account.account_type
                account_info = f"{entry.account.account_number} {entry.account.name}"
                
                if account_type == 'ASSET' and account_info not in asset_accounts:
                    asset_accounts.append(account_info)
                elif account_type == 'LIABILITY' and account_info not in liability_accounts:
                    liability_accounts.append(account_info)
                elif account_type == 'EQUITY' and account_info not in equity_accounts:
                    equity_accounts.append(account_info)
            
            print(f"  Asset accounts: {len(asset_accounts)}")
            for acc in asset_accounts:
                print(f"    {acc}")
            
            print(f"  Liability accounts: {len(liability_accounts)}")
            for acc in liability_accounts:
                print(f"    {acc}")
            
            print(f"  Equity accounts: {len(equity_accounts)}")
            for acc in equity_accounts:
                print(f"    {acc}")

def generate_balance_sheet(entity, as_of_date):
    """Generate balance sheet from ledger entries."""
    print(f"\nGenerating balance sheet for {entity.name} as of {as_of_date}")
    
    # Get all ledger entries up to the date
    entries = LedgerEntry.objects.filter(
        entity=entity,
        entry_date__lte=as_of_date
    )
    
    if entries.count() == 0:
        print("  No ledger entries found")
        return None
    
    # Calculate balances by account type
    accounts = {}
    
    for entry in entries:
        acc_key = entry.account.id
        if acc_key not in accounts:
            accounts[acc_key] = {
                'account': entry.account,
                'debit_total': Decimal('0'),
                'credit_total': Decimal('0')
            }
        
        if entry.entry_type == 'DEBIT':
            accounts[acc_key]['debit_total'] += entry.amount
        else:
            accounts[acc_key]['credit_total'] += entry.amount
    
    # Calculate net balances by type
    total_assets = Decimal('0')
    total_liabilities = Decimal('0')
    total_equity = Decimal('0')
    
    for acc_data in accounts.values():
        account = acc_data['account']
        net_balance = acc_data['debit_total'] - acc_data['credit_total']
        
        if account.account_type == 'ASSET':
            # Assets have normal debit balance
            if net_balance > 0:
                total_assets += net_balance
                print(f"  Asset: {account.name} = {net_balance}")
        elif account.account_type == 'LIABILITY':
            # Liabilities have normal credit balance
            if net_balance < 0:
                total_liabilities += abs(net_balance)
                print(f"  Liability: {account.name} = {abs(net_balance)}")
        elif account.account_type == 'EQUITY':
            # Equity has normal credit balance
            if net_balance < 0:
                total_equity += abs(net_balance)
                print(f"  Equity: {account.name} = {abs(net_balance)}")
    
    print(f"\nBalance Sheet Totals:")
    print(f"  Total Assets: {total_assets}")
    print(f"  Total Liabilities: {total_liabilities}")
    print(f"  Total Equity: {total_equity}")
    print(f"  Balance Check: Assets ({total_assets}) = Liab + Equity ({total_liabilities + total_equity})")
    
    # Create or update balance sheet record
    balance_sheet, created = BalanceSheet.objects.update_or_create(
        entity=entity,
        as_of_date=as_of_date,
        defaults={
            'total_assets': total_assets,
            'total_liabilities': total_liabilities,
            'total_equity': total_equity
        }
    )
    
    print(f"  {'Created' if created else 'Updated'} balance sheet record")
    return balance_sheet

if __name__ == '__main__':
    check_balance_sheet_data()
    
    # Generate balance sheets for entities with data
    print(f"\n=== GENERATING BALANCE SHEETS ===")
    
    today = date.today()
    tomorrow = date(2025, 12, 17)  # Since entries are on 2025-12-17
    
    for entity in Entity.objects.all():
        entries_count = LedgerEntry.objects.filter(entity=entity).count()
        if entries_count > 0:
            generate_balance_sheet(entity, tomorrow)
    
    print(f"\n=== DONE ===")