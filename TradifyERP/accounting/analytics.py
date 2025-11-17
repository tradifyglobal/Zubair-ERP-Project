"""Advanced analytics and reporting for accounting module."""
from django.db import models
from decimal import Decimal
from datetime import timedelta, datetime
from django.utils import timezone


class FinancialRatio:
    """Calculate key financial ratios."""
    
    @staticmethod
    def _get_account_balance(account):
        """Calculate account balance from opening_balance + ledger entries."""
        balance = account.opening_balance or Decimal('0')
        ledger_sum = account.ledger_entries.aggregate(
            total=models.Sum('amount')
        )['total'] or Decimal('0')
        return balance + ledger_sum
    
    @staticmethod
    def current_ratio(entity):
        """Current Assets / Current Liabilities"""
        current_assets = Decimal('0')
        for account in entity.accounts.filter(account_type='ASSET'):
            current_assets += FinancialRatio._get_account_balance(account)
        
        current_liabilities = Decimal('0')
        for account in entity.accounts.filter(account_type='LIABILITY'):
            current_liabilities += FinancialRatio._get_account_balance(account)
        
        if current_liabilities == 0:
            return None
        return float(current_assets / current_liabilities)
    
    @staticmethod
    def quick_ratio(entity):
        """(Current Assets - Inventory) / Current Liabilities"""
        current_assets = Decimal('0')
        for account in entity.accounts.filter(account_type='ASSET'):
            current_assets += FinancialRatio._get_account_balance(account)
        
        current_liabilities = Decimal('0')
        for account in entity.accounts.filter(account_type='LIABILITY'):
            current_liabilities += FinancialRatio._get_account_balance(account)
        
        if current_liabilities == 0:
            return None
        return float(current_assets / current_liabilities)
    
    @staticmethod
    def debt_to_equity(entity):
        """Total Liabilities / Total Equity"""
        total_liabilities = Decimal('0')
        for account in entity.accounts.filter(account_type='LIABILITY'):
            total_liabilities += FinancialRatio._get_account_balance(account)
        
        total_equity = Decimal('1')
        for account in entity.accounts.filter(account_type='EQUITY'):
            total_equity += FinancialRatio._get_account_balance(account)
        
        if total_equity == 0:
            return None
        return float(total_liabilities / total_equity)
    
    @staticmethod
    def debt_ratio(entity):
        """Total Liabilities / Total Assets"""
        total_liabilities = Decimal('0')
        for account in entity.accounts.filter(account_type='LIABILITY'):
            total_liabilities += FinancialRatio._get_account_balance(account)
        
        total_assets = Decimal('1')
        for account in entity.accounts.filter(account_type='ASSET'):
            total_assets += FinancialRatio._get_account_balance(account)
        
        if total_assets == 0:
            return None
        return float((total_liabilities / total_assets) * 100)
    
    @staticmethod
    def gross_profit_margin(entity):
        """(Revenue - COGS) / Revenue"""
        from .models import LedgerEntry
        
        # Get revenue
        revenue = Decimal('0')
        for account in entity.accounts.filter(account_type='REVENUE'):
            revenue += FinancialRatio._get_account_balance(account)
        
        if revenue == 0:
            return None
        gross_profit = revenue
        return float((gross_profit / revenue) * 100) if revenue > 0 else None
    
    @staticmethod
    def get_all_ratios(entity):
        """Get all key financial ratios."""
        return {
            'current_ratio': FinancialRatio.current_ratio(entity),
            'quick_ratio': FinancialRatio.quick_ratio(entity),
            'debt_to_equity': FinancialRatio.debt_to_equity(entity),
            'debt_ratio': FinancialRatio.debt_ratio(entity),
            'gross_profit_margin': FinancialRatio.gross_profit_margin(entity),
        }


class AgingReport:
    """Generate aging reports for AR and AP."""
    
    @staticmethod
    def accounts_receivable_aging(entity, as_of_date=None):
        """Generate aging report for accounts receivable."""
        if as_of_date is None:
            as_of_date = timezone.now().date()
        
        from .models import Customer, VendorInvoice
        
        aging_data = {
            'current': Decimal('0'),      # 0-30 days
            '31_60': Decimal('0'),        # 31-60 days
            '61_90': Decimal('0'),        # 61-90 days
            'over_90': Decimal('0'),      # Over 90 days
        }
        
        invoices = VendorInvoice.objects.filter(
            entity=entity,
            invoice_date__lte=as_of_date
        )
        
        for invoice in invoices:
            days_outstanding = (as_of_date - invoice.invoice_date).days
            remaining_balance = invoice.total_amount - invoice.amount_paid
            
            if remaining_balance <= 0:
                continue
            
            if days_outstanding <= 30:
                aging_data['current'] += remaining_balance
            elif days_outstanding <= 60:
                aging_data['31_60'] += remaining_balance
            elif days_outstanding <= 90:
                aging_data['61_90'] += remaining_balance
            else:
                aging_data['over_90'] += remaining_balance
        
        return aging_data
    
    @staticmethod
    def accounts_payable_aging(entity, as_of_date=None):
        """Generate aging report for accounts payable."""
        if as_of_date is None:
            as_of_date = timezone.now().date()
        
        from .models import VendorInvoice
        
        aging_data = {
            'current': Decimal('0'),
            '31_60': Decimal('0'),
            '61_90': Decimal('0'),
            'over_90': Decimal('0'),
        }
        
        invoices = VendorInvoice.objects.filter(
            entity=entity,
            invoice_date__lte=as_of_date
        )
        
        for invoice in invoices:
            days_outstanding = (as_of_date - invoice.invoice_date).days
            remaining_balance = invoice.total_amount - invoice.amount_paid
            
            if remaining_balance <= 0:
                continue
            
            if days_outstanding <= 30:
                aging_data['current'] += remaining_balance
            elif days_outstanding <= 60:
                aging_data['31_60'] += remaining_balance
            elif days_outstanding <= 90:
                aging_data['61_90'] += remaining_balance
            else:
                aging_data['over_90'] += remaining_balance
        
        return aging_data


class VarianceAnalysis:
    """Budget vs Actual variance analysis."""
    
    @staticmethod
    def calculate_variance(entity, period_start, period_end):
        """Calculate variance between budgeted and actual amounts."""
        from .models import LedgerEntry, Account
        
        variance_data = []
        
        for account in entity.accounts.all():
            actual_amount = account.ledger_entries.filter(
                entry_date__gte=period_start,
                entry_date__lte=period_end
            ).aggregate(
                total=models.Sum('amount')
            )['total'] or Decimal('0')
            
            # Budget would come from a Budget model (not implemented yet)
            budget_amount = Decimal('0')
            
            variance = actual_amount - budget_amount
            variance_pct = (variance / budget_amount * 100) if budget_amount != 0 else 0
            
            variance_data.append({
                'account': account,
                'budget': budget_amount,
                'actual': actual_amount,
                'variance': variance,
                'variance_pct': variance_pct,
            })
        
        return variance_data


class CostCenterAnalysis:
    """Analyze costs by cost center."""
    
    @staticmethod
    def get_cost_by_center(entity, period_start, period_end):
        """Get expenses by cost center."""
        from .models import LedgerEntry
        
        cost_data = {}
        
        expenses = LedgerEntry.objects.filter(
            entity=entity,
            account__account_type='EXPENSE',
            entry_date__gte=period_start,
            entry_date__lte=period_end
        )
        
        for expense in expenses:
            center = expense.account.name  # Would use cost_center field if available
            if center not in cost_data:
                cost_data[center] = Decimal('0')
            cost_data[center] += expense.amount
        
        return cost_data
