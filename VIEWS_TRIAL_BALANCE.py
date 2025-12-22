"""
TRIAL BALANCE VIEWS - PRODUCTION COMPATIBLE
Display and generate trial balance reports
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, Q
from django.http import HttpResponse
from django.utils import timezone
from decimal import Decimal
from datetime import datetime
import csv

from accounting.models import TrialBalance, Entity, Account
from accounting.mixins import SessionEntityMixin


class TrialBalanceListView(SessionEntityMixin, LoginRequiredMixin, ListView):
    """
    List all trial balances
    """
    model = TrialBalance
    template_name = 'accounting/trial_balance_list.html'
    context_object_name = 'trial_balances'
    paginate_by = 20
    
    def get_queryset(self):
        # SessionEntityMixin will automatically filter by entity
        queryset = super().get_queryset().order_by('-as_of_date')
        
        # Filter by date range if provided
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        
        if start_date:
            queryset = queryset.filter(as_of_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(as_of_date__lte=end_date)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        entity = self.request.entity
        context['total_count'] = TrialBalance.objects.filter(entity=entity).count()
        context['balanced_count'] = TrialBalance.objects.filter(entity=entity, is_balanced=True).count()
        context['unbalanced_count'] = TrialBalance.objects.filter(entity=entity, is_balanced=False).count()
        return context


class TrialBalanceDetailView(SessionEntityMixin, LoginRequiredMixin, DetailView):
    """
    Display detailed trial balance information
    """
    model = TrialBalance
    template_name = 'accounting/trial_balance_detail.html'
    context_object_name = 'trial_balance'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tb = self.get_object()
        
        # Calculate actual trial balance data
        from accounting.trial_balance import calculate_trial_balance
        from decimal import Decimal
        
        tb_data = calculate_trial_balance(tb.entity, tb.as_of_date)
        
        if tb_data:
            account_balances = tb_data.get('account_balances', [])
            
            # Group accounts by type
            assets_lines = []
            liabilities_lines = []
            equity_lines = []
            income_lines = []
            expenses_lines = []
            
            # Get account objects for display
            from accounting.models import Account
            
            for acc_bal in account_balances:
                # Get account object
                try:
                    account = Account.objects.get(id=acc_bal['account_id'])
                except Account.DoesNotExist:
                    continue
                
                line_data = {
                    'account': account,
                    'debit_amount': acc_bal.get('debit_balance', Decimal('0')),
                    'credit_amount': acc_bal.get('credit_balance', Decimal('0')),
                    'balance': acc_bal.get('debit_balance', Decimal('0')) - acc_bal.get('credit_balance', Decimal('0'))
                }
                
                acc_type = acc_bal['account_type']
                if acc_type == 'ASSET':
                    assets_lines.append(line_data)
                elif acc_type == 'LIABILITY':
                    liabilities_lines.append(line_data)
                elif acc_type == 'EQUITY':
                    equity_lines.append(line_data)
                elif acc_type == 'INCOME':
                    income_lines.append(line_data)
                elif acc_type == 'EXPENSE':
                    expenses_lines.append(line_data)
            
            # Calculate totals for each type
            context['assets_lines'] = assets_lines
            context['liabilities_lines'] = liabilities_lines
            context['equity_lines'] = equity_lines
            context['income_lines'] = income_lines
            context['expenses_lines'] = expenses_lines
            
            context['assets_count'] = len(assets_lines)
            context['liabilities_count'] = len(liabilities_lines)
            context['equity_count'] = len(equity_lines)
            context['income_count'] = len(income_lines)
            context['expenses_count'] = len(expenses_lines)
            
            # Calculate totals
            context['assets_debit'] = sum(line['debit_amount'] for line in assets_lines)
            context['assets_credit'] = sum(line['credit_amount'] for line in assets_lines)
            context['assets_balance'] = sum(line['balance'] for line in assets_lines)
            
            context['liabilities_debit'] = sum(line['debit_amount'] for line in liabilities_lines)
            context['liabilities_credit'] = sum(line['credit_amount'] for line in liabilities_lines)
            context['liabilities_balance'] = sum(line['balance'] for line in liabilities_lines)
            
            context['equity_debit'] = sum(line['debit_amount'] for line in equity_lines)
            context['equity_credit'] = sum(line['credit_amount'] for line in equity_lines)
            context['equity_balance'] = sum(line['balance'] for line in equity_lines)
            
            context['income_debit'] = sum(line['debit_amount'] for line in income_lines)
            context['income_credit'] = sum(line['credit_amount'] for line in income_lines)
            context['income_balance'] = sum(line['balance'] for line in income_lines)
            
            context['expenses_debit'] = sum(line['debit_amount'] for line in expenses_lines)
            context['expenses_credit'] = sum(line['credit_amount'] for line in expenses_lines)
            context['expenses_balance'] = sum(line['balance'] for line in expenses_lines)
        
        context['is_balanced'] = tb.is_balanced
        context['status_class'] = 'success' if tb.is_balanced else 'danger'
        
        return context


class TrialBalanceDashboardView(SessionEntityMixin, LoginRequiredMixin, TemplateView):
    """
    Trial Balance Dashboard - Overview
    """
    template_name = 'accounting/trial_balance_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        entity = self.request.entity
        
        # Get latest TB for selected entity
        latest_tb = TrialBalance.objects.filter(entity=entity).order_by('-as_of_date').first()
        context['latest_tb'] = latest_tb
        
        # Statistics for selected entity
        context['total_count'] = TrialBalance.objects.filter(entity=entity).count()
        context['balanced_count'] = TrialBalance.objects.filter(entity=entity, is_balanced=True).count()
        context['unbalanced_count'] = TrialBalance.objects.filter(entity=entity, is_balanced=False).count()
        
        # Recent TBs for selected entity
        context['recent_tbs'] = TrialBalance.objects.filter(entity=entity).order_by('-as_of_date')[:10]
        
        # Only show current entity stats (removed multi-entity display)
        
        return context


class MonthlyTrialBalanceListView(SessionEntityMixin, LoginRequiredMixin, ListView):
    """
    List monthly trial balance archives
    """
    model = TrialBalance
    template_name = 'accounting/monthly_trial_balance_list.html'
    context_object_name = 'trial_balances'
    paginate_by = 12
    
    def get_queryset(self):
        # SessionEntityMixin will filter by entity automatically
        return super().get_queryset().order_by('-as_of_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        entity = self.request.entity
        context['total_count'] = TrialBalance.objects.filter(entity=entity).count()
        context['balanced_count'] = TrialBalance.objects.filter(entity=entity, is_balanced=True).count()
        context['unbalanced_count'] = TrialBalance.objects.filter(entity=entity, is_balanced=False).count()
        return context


class TrialBalanceReportView(SessionEntityMixin, LoginRequiredMixin, TemplateView):
    """
    Display trial balance as a financial report
    """
    template_name = 'accounting/trial_balance_report.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        entity = self.request.entity
        
        # Get latest TB or from date param for selected entity
        tb_id = self.request.GET.get('tb_id')
        if tb_id:
            try:
                tb = TrialBalance.objects.get(id=tb_id, entity=entity)
            except TrialBalance.DoesNotExist:
                tb = TrialBalance.objects.filter(entity=entity).order_by('-as_of_date').first()
        else:
            tb = TrialBalance.objects.filter(entity=entity).order_by('-as_of_date').first()
        
        context['trial_balance'] = tb
        context['is_balanced'] = tb.is_balanced if tb else False
        
        return context


class TrialBalanceComparisonView(SessionEntityMixin, LoginRequiredMixin, TemplateView):
    """
    Compare two trial balance periods
    """
    template_name = 'accounting/trial_balance_comparison.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        entity = self.request.entity
        
        # Only show TBs for selected entity
        all_tbs = TrialBalance.objects.filter(entity=entity).order_by('-as_of_date')
        context['available_tbs'] = all_tbs
        
        # Get comparison TBs if specified
        from_id = self.request.GET.get('from_id')
        to_id = self.request.GET.get('to_id')
        
        if from_id and to_id:
            try:
                from_tb = TrialBalance.objects.get(id=from_id, entity=entity)
                to_tb = TrialBalance.objects.get(id=to_id, entity=entity)
                context['from_tb'] = from_tb
                context['to_tb'] = to_tb
            except TrialBalance.DoesNotExist:
                pass
        
        return context


class TrialBalanceExportView(SessionEntityMixin, LoginRequiredMixin, DetailView):
    """
    Export trial balance to CSV
    """
    model = TrialBalance
    
    def render_to_response(self, context, **response_kwargs):
        tb = self.get_object()
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="trial_balance_{tb.as_of_date}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Trial Balance Report', tb.as_of_date])
        writer.writerow(['Entity', tb.entity.name])
        writer.writerow(['Balanced', 'Yes' if tb.is_balanced else 'No'])
        writer.writerow([])
        writer.writerow(['Account Code', 'Account Name', 'Type', 'Debit', 'Credit'])
        
        # Get accounts
        accounts = Account.objects.filter(entity=tb.entity, is_active=True).order_by('account_type', 'code')
        
        total_debit = Decimal('0.00')
        total_credit = Decimal('0.00')
        
        for account in accounts:
            writer.writerow([
                account.code,
                account.name,
                account.account_type,
                tb.total_debits,
                tb.total_credits
            ])
            total_debit += tb.total_debits
            total_credit += tb.total_credits
        
        writer.writerow([])
        writer.writerow(['TOTAL', '', '', total_debit, total_credit])
        
        return response

