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


class TrialBalanceListView(LoginRequiredMixin, ListView):
    """
    List all trial balances
    """
    model = TrialBalance
    template_name = 'accounting/trial_balance_list.html'
    context_object_name = 'trial_balances'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = TrialBalance.objects.all().order_by('-as_of_date')
        
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
        context['total_count'] = TrialBalance.objects.count()
        context['balanced_count'] = TrialBalance.objects.filter(is_balanced=True).count()
        context['unbalanced_count'] = TrialBalance.objects.filter(is_balanced=False).count()
        return context


class TrialBalanceDetailView(LoginRequiredMixin, DetailView):
    """
    Display detailed trial balance information
    """
    model = TrialBalance
    template_name = 'accounting/trial_balance_detail.html'
    context_object_name = 'trial_balance'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tb = self.get_object()
        
        # Get accounts for this entity
        accounts = Account.objects.filter(entity=tb.entity, is_active=True)
        
        # Group by type
        account_groups = {
            'ASSET': [],
            'LIABILITY': [],
            'EQUITY': [],
            'INCOME': [],
            'EXPENSE': [],
        }
        
        for account in accounts:
            acc_type = account.account_type
            if acc_type in account_groups:
                account_groups[acc_type].append(account)
        
        context['account_groups'] = account_groups
        context['is_balanced'] = tb.is_balanced
        context['status_class'] = 'success' if tb.is_balanced else 'danger'
        
        return context


class TrialBalanceDashboardView(LoginRequiredMixin, TemplateView):
    """
    Trial Balance Dashboard - Overview
    """
    template_name = 'accounting/trial_balance_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get latest TB
        latest_tb = TrialBalance.objects.order_by('-as_of_date').first()
        context['latest_tb'] = latest_tb
        
        # Statistics
        context['total_count'] = TrialBalance.objects.count()
        context['balanced_count'] = TrialBalance.objects.filter(is_balanced=True).count()
        context['unbalanced_count'] = TrialBalance.objects.filter(is_balanced=False).count()
        
        # Recent TBs
        context['recent_tbs'] = TrialBalance.objects.order_by('-as_of_date')[:10]
        
        # By entity
        context['by_entity'] = {}
        for entity in Entity.objects.all():
            tbs = TrialBalance.objects.filter(entity=entity)
            if tbs.exists():
                latest = tbs.order_by('-as_of_date').first()
                context['by_entity'][entity.name] = {
                    'count': tbs.count(),
                    'latest': latest,
                    'is_balanced': latest.is_balanced
                }
        
        return context


class MonthlyTrialBalanceListView(LoginRequiredMixin, ListView):
    """
    List monthly trial balance archives
    """
    model = TrialBalance
    template_name = 'accounting/monthly_trial_balance_list.html'
    context_object_name = 'trial_balances'
    paginate_by = 12
    
    def get_queryset(self):
        return TrialBalance.objects.order_by('-as_of_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_count'] = TrialBalance.objects.count()
        context['balanced_count'] = TrialBalance.objects.filter(is_balanced=True).count()
        context['unbalanced_count'] = TrialBalance.objects.filter(is_balanced=False).count()
        return context


class TrialBalanceReportView(LoginRequiredMixin, TemplateView):
    """
    Display trial balance as a financial report
    """
    template_name = 'accounting/trial_balance_report.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get latest TB or from date param
        tb_id = self.request.GET.get('tb_id')
        if tb_id:
            try:
                tb = TrialBalance.objects.get(id=tb_id)
            except TrialBalance.DoesNotExist:
                tb = TrialBalance.objects.order_by('-as_of_date').first()
        else:
            tb = TrialBalance.objects.order_by('-as_of_date').first()
        
        context['trial_balance'] = tb
        context['is_balanced'] = tb.is_balanced if tb else False
        
        return context


class TrialBalanceComparisonView(LoginRequiredMixin, TemplateView):
    """
    Compare two trial balance periods
    """
    template_name = 'accounting/trial_balance_comparison.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        all_tbs = TrialBalance.objects.order_by('-as_of_date')
        context['available_tbs'] = all_tbs
        
        # Get comparison TBs if specified
        from_id = self.request.GET.get('from_id')
        to_id = self.request.GET.get('to_id')
        
        if from_id and to_id:
            try:
                from_tb = TrialBalance.objects.get(id=from_id)
                to_tb = TrialBalance.objects.get(id=to_id)
                context['from_tb'] = from_tb
                context['to_tb'] = to_tb
            except TrialBalance.DoesNotExist:
                pass
        
        return context


class TrialBalanceExportView(LoginRequiredMixin, DetailView):
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
