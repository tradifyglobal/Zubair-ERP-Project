#!/usr/bin/env python3

import os
import sys
import django

sys.path.append('/var/www/tradifyerp')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from accounting.models import Entity, ProfitLossReport, LedgerEntry, Account
from decimal import Decimal
from datetime import date

def check_profit_loss_data():
    print("=== PROFIT & LOSS DATA ANALYSIS ===")
    
    entities = Entity.objects.all()
    
    for entity in entities:
        print(f"\nEntity: {entity.name} (ID: {entity.id})")
        
        # Check existing P&L records
        pl_records = ProfitLossReport.objects.filter(entity=entity)
        print(f"  Existing P&L records: {pl_records.count()}")
        
        for pl in pl_records:
            print(f"    {pl.period_start} to {pl.period_end}: Income {pl.total_income} | Expenses {pl.total_expenses} | Net {pl.net_profit}")
        
        # Check ledger entries for income/expense accounts
        ledger_entries = LedgerEntry.objects.filter(entity=entity)
        print(f"  Ledger entries: {ledger_entries.count()}")
        
        if ledger_entries.count() > 0:
            # Categorize accounts by type
            income_accounts = []
            expense_accounts = []
            
            for entry in ledger_entries:
                account_type = entry.account.account_type
                account_info = f"{entry.account.account_number} {entry.account.name}"
                
                if account_type == 'INCOME' and account_info not in income_accounts:
                    income_accounts.append(account_info)
                elif account_type == 'EXPENSE' and account_info not in expense_accounts:
                    expense_accounts.append(account_info)
            
            print(f"  Income accounts: {len(income_accounts)}")
            for acc in income_accounts:
                print(f"    {acc}")
            
            print(f"  Expense accounts: {len(expense_accounts)}")
            for acc in expense_accounts:
                print(f"    {acc}")
                
            # Note: The Test entity only has ASSET and EQUITY accounts, no INCOME/EXPENSE
            # This explains why there's no P&L data!

def generate_profit_loss(entity, period_start, period_end):
    """Generate P&L from ledger entries."""
    print(f"\nGenerating P&L for {entity.name} from {period_start} to {period_end}")
    
    # Get all ledger entries in the period
    entries = LedgerEntry.objects.filter(
        entity=entity,
        entry_date__gte=period_start,
        entry_date__lte=period_end
    )
    
    if entries.count() == 0:
        print("  No ledger entries found in this period")
        return None
    
    # Calculate income and expense totals
    total_income = Decimal('0')
    total_expenses = Decimal('0')
    
    income_details = []
    expense_details = []
    
    # Group by account
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
    
    # Process by account type
    for acc_data in accounts.values():
        account = acc_data['account']
        net_balance = acc_data['debit_total'] - acc_data['credit_total']
        
        if account.account_type == 'INCOME':
            # Income accounts have normal credit balance
            if net_balance < 0:
                income_amount = abs(net_balance)
                total_income += income_amount
                income_details.append({
                    'name': account.name,
                    'number': account.account_number,
                    'amount': income_amount
                })
                print(f"  Income: {account.name} = {income_amount}")
                
        elif account.account_type == 'EXPENSE':
            # Expense accounts have normal debit balance
            if net_balance > 0:
                total_expenses += net_balance
                expense_details.append({
                    'name': account.name,
                    'number': account.account_number,
                    'amount': net_balance
                })
                print(f"  Expense: {account.name} = {net_balance}")
    
    net_profit = total_income - total_expenses
    
    print(f"\nP&L Summary:")
    print(f"  Total Income: {total_income}")
    print(f"  Total Expenses: {total_expenses}")
    print(f"  Net Profit: {net_profit}")
    
    if total_income == 0 and total_expenses == 0:
        print("  No income or expense transactions found - cannot generate P&L")
        return None
    
    # Create or update P&L record
    pl_report, created = ProfitLossReport.objects.update_or_create(
        entity=entity,
        period_start=period_start,
        period_end=period_end,
        defaults={
            'total_income': total_income,
            'total_expenses': total_expenses,
            'net_profit': net_profit
        }
    )
    
    print(f"  {'Created' if created else 'Updated'} P&L record")
    return pl_report

if __name__ == '__main__':
    check_profit_loss_data()
    
    # Try to generate P&L for entities with data
    print(f"\n=== ATTEMPTING P&L GENERATION ===")
    
    from datetime import date
    start_date = date(2025, 12, 1)
    end_date = date(2025, 12, 17)
    
    for entity in Entity.objects.all():
        entries_count = LedgerEntry.objects.filter(entity=entity).count()
        if entries_count > 0:
            generate_profit_loss(entity, start_date, end_date)
    
    print(f"\n=== DONE ===")