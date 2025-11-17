"""
Accounting Module - P&L Report Generator
Automatically calculates P&L from GL entries, including Sales module data.
"""

from decimal import Decimal
from django.db.models import Sum
from datetime import datetime
from accounting.models import Entity, Account, LedgerEntry, ProfitLossReport


def calculate_pl_from_gl(entity, period_start, period_end):
    """
    Calculate P&L directly from GL entries for accurate financial reporting.
    
    Includes:
    - Sales Revenue (from Sales module)
    - Cost of Goods Sold
    - Operating Expenses
    - Other Income/Expenses
    
    Returns dictionary with all P&L line items and totals.
    """
    
    try:
        pl_data = {
            'entity': entity,
            'period_start': period_start,
            'period_end': period_end,
            'lines': {},
            'subtotals': {},
            'totals': {},
        }
        
        # Get all INCOME and EXPENSE accounts for this entity
        income_accounts = Account.objects.filter(
            entity=entity,
            account_type='INCOME',
            is_active=True
        ).order_by('account_number')
        
        expense_accounts = Account.objects.filter(
            entity=entity,
            account_type='EXPENSE',
            is_active=True
        ).order_by('account_number')
        
        # Calculate REVENUE (INCOME accounts)
        total_revenue = Decimal('0.00')
        revenue_items = []
        
        for account in income_accounts:
            # For income accounts, CREDITS increase income, DEBITS decrease it
            credits = LedgerEntry.objects.filter(
                account=account,
                entity=entity,
                entry_date__gte=period_start,
                entry_date__lte=period_end,
                entry_type='CREDIT',
                is_posted=True
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            
            debits = LedgerEntry.objects.filter(
                account=account,
                entity=entity,
                entry_date__gte=period_start,
                entry_date__lte=period_end,
                entry_type='DEBIT',
                is_posted=True
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            
            account_balance = credits - debits
            
            if account_balance != Decimal('0.00'):
                revenue_items.append({
                    'account_number': account.account_number,
                    'account_name': account.name,
                    'amount': account_balance,
                })
                total_revenue += account_balance
        
        pl_data['lines']['revenue'] = revenue_items
        pl_data['subtotals']['total_revenue'] = total_revenue
        
        # Calculate EXPENSES (EXPENSE accounts)
        total_expenses = Decimal('0.00')
        expense_items = []
        
        for account in expense_accounts:
            # For expense accounts, DEBITS increase expenses, CREDITS decrease it
            debits = LedgerEntry.objects.filter(
                account=account,
                entity=entity,
                entry_date__gte=period_start,
                entry_date__lte=period_end,
                entry_type='DEBIT',
                is_posted=True
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            
            credits = LedgerEntry.objects.filter(
                account=account,
                entity=entity,
                entry_date__gte=period_start,
                entry_date__lte=period_end,
                entry_type='CREDIT',
                is_posted=True
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            
            account_balance = debits - credits
            
            if account_balance != Decimal('0.00'):
                expense_items.append({
                    'account_number': account.account_number,
                    'account_name': account.name,
                    'amount': account_balance,
                })
                total_expenses += account_balance
        
        pl_data['lines']['expenses'] = expense_items
        pl_data['subtotals']['total_expenses'] = total_expenses
        
        # Calculate NET PROFIT
        net_profit = total_revenue - total_expenses
        pl_data['totals']['net_profit'] = net_profit
        pl_data['totals']['total_revenue'] = total_revenue
        pl_data['totals']['total_expenses'] = total_expenses
        
        # Additional metrics for analysis
        if total_revenue > 0:
            expense_ratio = (total_expenses / total_revenue) * 100
            profit_margin = (net_profit / total_revenue) * 100
        else:
            expense_ratio = Decimal('0.00')
            profit_margin = Decimal('0.00')
        
        pl_data['metrics'] = {
            'expense_ratio': expense_ratio,  # % of revenue spent on expenses
            'profit_margin': profit_margin,   # % profit on revenue
            'revenue_count': len(revenue_items),
            'expense_count': len(expense_items),
        }
        
        return pl_data
    
    except Exception as e:
        print(f"Error calculating P&L from GL: {str(e)}")
        return {
            'error': str(e),
            'entity': entity,
            'period_start': period_start,
            'period_end': period_end,
        }


def generate_pl_report(entity, period_start, period_end):
    """
    Generate and save P&L report to database from GL entries.
    
    Creates a ProfitLossReport record with calculated totals.
    """
    try:
        # Calculate P&L from GL
        pl_data = calculate_pl_from_gl(entity, period_start, period_end)
        
        if 'error' in pl_data:
            return None
        
        # Create or update ProfitLossReport
        pl_report, created = ProfitLossReport.objects.update_or_create(
            entity=entity,
            period_start=period_start,
            period_end=period_end,
            defaults={
                'total_income': pl_data['subtotals']['total_revenue'],
                'total_expenses': pl_data['subtotals']['total_expenses'],
                'net_profit': pl_data['totals']['net_profit'],
            }
        )
        
        return pl_report
    
    except Exception as e:
        print(f"Error generating P&L report: {str(e)}")
        return None


def get_sales_revenue_for_period(entity, period_start, period_end):
    """
    Get Sales Revenue (from Sales module GL entries) for a period.
    
    This specifically pulls from the 4100 Sales Revenue account.
    Used for Sales-specific reporting and P&L breakdown.
    """
    try:
        # Get Sales Revenue account (4100)
        sales_revenue_account = Account.objects.filter(
            entity=entity,
            account_number='4100',
            account_type='INCOME'
        ).first()
        
        if not sales_revenue_account:
            return Decimal('0.00')
        
        # Calculate revenue for period
        credits = LedgerEntry.objects.filter(
            account=sales_revenue_account,
            entity=entity,
            entry_date__gte=period_start,
            entry_date__lte=period_end,
            entry_type='CREDIT',
            is_posted=True
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        debits = LedgerEntry.objects.filter(
            account=sales_revenue_account,
            entity=entity,
            entry_date__gte=period_start,
            entry_date__lte=period_end,
            entry_type='DEBIT',
            is_posted=True
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        revenue = credits - debits
        return max(revenue, Decimal('0.00'))
    
    except Exception as e:
        print(f"Error getting sales revenue: {str(e)}")
        return Decimal('0.00')


def get_tax_summary_for_period(entity, period_start, period_end):
    """
    Get Sales Tax summary from GL (2110 Sales Tax Payable account).
    Used for tax reporting and compliance.
    """
    try:
        # Get Sales Tax Payable account (2110)
        tax_account = Account.objects.filter(
            entity=entity,
            account_number='2110',
            account_type='LIABILITY'
        ).first()
        
        if not tax_account:
            return {
                'tax_collected': Decimal('0.00'),
                'tax_paid': Decimal('0.00'),
                'tax_outstanding': Decimal('0.00'),
            }
        
        # For liability accounts, CREDITS increase liability, DEBITS decrease it
        credits = LedgerEntry.objects.filter(
            account=tax_account,
            entity=entity,
            entry_date__gte=period_start,
            entry_date__lte=period_end,
            entry_type='CREDIT',
            is_posted=True
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        debits = LedgerEntry.objects.filter(
            account=tax_account,
            entity=entity,
            entry_date__gte=period_start,
            entry_date__lte=period_end,
            entry_type='DEBIT',
            is_posted=True
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        tax_collected = credits
        tax_paid = debits
        tax_outstanding = credits - debits
        
        return {
            'tax_collected': max(tax_collected, Decimal('0.00')),
            'tax_paid': max(tax_paid, Decimal('0.00')),
            'tax_outstanding': max(tax_outstanding, Decimal('0.00')),
        }
    
    except Exception as e:
        print(f"Error getting tax summary: {str(e)}")
        return {
            'tax_collected': Decimal('0.00'),
            'tax_paid': Decimal('0.00'),
            'tax_outstanding': Decimal('0.00'),
        }


def get_ar_balance_for_period(entity, period_start, period_end):
    """
    Get Accounts Receivable balance (1200 account) as of period_end.
    Shows outstanding customer invoices from Sales module.
    """
    try:
        # Get AR account (1200)
        ar_account = Account.objects.filter(
            entity=entity,
            account_number='1200',
            account_type='ASSET'
        ).first()
        
        if not ar_account:
            return Decimal('0.00')
        
        # For asset accounts, DEBITS increase, CREDITS decrease
        debits = LedgerEntry.objects.filter(
            account=ar_account,
            entity=entity,
            entry_date__lte=period_end,
            entry_type='DEBIT',
            is_posted=True
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        credits = LedgerEntry.objects.filter(
            account=ar_account,
            entity=entity,
            entry_date__lte=period_end,
            entry_type='CREDIT',
            is_posted=True
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        ar_balance = debits - credits
        return max(ar_balance, Decimal('0.00'))
    
    except Exception as e:
        print(f"Error getting AR balance: {str(e)}")
        return Decimal('0.00')


def get_pl_comparison(entity, periods):
    """
    Compare P&L across multiple periods for trend analysis.
    
    periods: List of (period_start, period_end) tuples
    Returns list of P&L dictionaries for comparison.
    """
    try:
        comparison_data = []
        
        for period_start, period_end in periods:
            pl_data = calculate_pl_from_gl(entity, period_start, period_end)
            
            if 'error' not in pl_data:
                comparison_data.append({
                    'period': f"{period_start} to {period_end}",
                    'period_start': period_start,
                    'period_end': period_end,
                    'revenue': pl_data['subtotals']['total_revenue'],
                    'expenses': pl_data['subtotals']['total_expenses'],
                    'profit': pl_data['totals']['net_profit'],
                    'profit_margin': pl_data['metrics']['profit_margin'],
                })
        
        return comparison_data
    
    except Exception as e:
        print(f"Error comparing P&L periods: {str(e)}")
        return []
