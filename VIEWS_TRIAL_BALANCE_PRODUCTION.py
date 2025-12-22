"""
TRIAL BALANCE VIEWS - ADAPTED FOR PRODUCTION MODELS
Display and generate trial balance reports
Adapted to work with existing TrialBalance model
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, TemplateView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import Sum, Q, F
from django.http import JsonResponse, HttpResponse
from django.urls import reverse_lazy
from django.utils import timezone
from decimal import Decimal
from datetime import datetime, timedelta
import csv

from accounting.models import TrialBalance, Account, LedgerEntry
from accounting.mixins import SessionEntityMixin


class TrialBalanceListView(LoginRequiredMixin, SessionEntityMixin, ListView):
    """
    List all trial balances for entity
    """
    model = TrialBalance
    template_name = 'accounting/trial_balance_list.html'
    context_object_name = 'trial_balances'
    paginate_by = 20
    
    def get_queryset(self):
        return TrialBalance.objects.filter(
            entity=self.entity
        ).order_by('-as_of_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Latest trial balance
        latest_tb = TrialBalance.objects.filter(
            entity=self.entity
        ).order_by('-as_of_date').first()
        
        # Balanced vs Unbalanced count
        balanced_count = TrialBalance.objects.filter(
            entity=self.entity,
            is_balanced=True
        ).count()
        
        unbalanced_count = TrialBalance.objects.filter(
            entity=self.entity,
            is_balanced=False
        ).count()
        
        context['latest_tb'] = latest_tb
        context['balanced_count'] = balanced_count
        context['unbalanced_count'] = unbalanced_count
        
        return context


class TrialBalanceDetailView(LoginRequiredMixin, SessionEntityMixin, DetailView):
    """
    View trial balance detail with account breakdown
    """
    model = TrialBalance
    template_name = 'accounting/trial_balance_detail.html'
    context_object_name = 'trial_balance'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tb = self.object
        
        # Get GL accounts with balances as of this date
        accounts_by_type = {}
        gl_accounts = Account.objects.filter(entity=tb.entity).values_list('account_type', 'id', 'account_code', 'name')
        
        for account_type, account_id, code, name in gl_accounts:
            # Calculate balance as of the trial balance date
            ledger_entries = LedgerEntry.objects.filter(
                account_id=account_id,
                journal_entry__posting_date__lte=tb.as_of_date,
                journal_entry__status='POSTED'
            )
            
            debit_sum = ledger_entries.filter(entry_type='DEBIT').aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
            credit_sum = ledger_entries.filter(entry_type='CREDIT').aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
            
            balance = debit_sum - credit_sum
            
            if account_type not in accounts_by_type:
                accounts_by_type[account_type] = []
            
            accounts_by_type[account_type].append({
                'account_id': account_id,
                'code': code,
                'name': name,
                'debit': debit_sum if balance > 0 else Decimal('0.00'),
                'credit': credit_sum if balance < 0 else Decimal('0.00'),
                'balance': abs(balance)
            })
        
        context['accounts_by_type'] = accounts_by_type
        return context


class TrialBalanceGenerateView(LoginRequiredMixin, SessionEntityMixin, FormView):
    """
    Generate new trial balance
    """
    template_name = 'accounting/trial_balance_generate.html'
    
    def post(self, request, *args, **kwargs):
        as_of_date = request.POST.get('as_of_date', timezone.now().date())
        
        # Calculate totals from GL
        debit_sum = Decimal('0.00')
        credit_sum = Decimal('0.00')
        
        gl_accounts = Account.objects.filter(entity=self.entity)
        for account in gl_accounts:
            ledger_entries = LedgerEntry.objects.filter(
                account=account,
                journal_entry__posting_date__lte=as_of_date,
                journal_entry__status='POSTED'
            )
            debit_sum += ledger_entries.filter(entry_type='DEBIT').aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
            credit_sum += ledger_entries.filter(entry_type='CREDIT').aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
        
        is_balanced = debit_sum == credit_sum
        
        # Create or update trial balance
        tb, created = TrialBalance.objects.get_or_create(
            entity=self.entity,
            as_of_date=as_of_date,
            defaults={
                'total_debits': debit_sum,
                'total_credits': credit_sum,
                'is_balanced': is_balanced
            }
        )
        
        if not created:
            tb.total_debits = debit_sum
            tb.total_credits = credit_sum
            tb.is_balanced = is_balanced
            tb.save()
        
        return redirect('accounting:trial_balance_detail', pk=tb.id)


class TrialBalanceReportView(LoginRequiredMixin, SessionEntityMixin, TemplateView):
    """
    Trial balance in financial statement format
    """
    template_name = 'accounting/trial_balance_report.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tb_id = self.kwargs.get('pk')
        tb = get_object_or_404(TrialBalance, id=tb_id, entity=self.entity)
        
        context['trial_balance'] = tb
        return context


class TrialBalanceComparisonView(LoginRequiredMixin, SessionEntityMixin, TemplateView):
    """
    Compare trial balances for two periods
    """
    template_name = 'accounting/trial_balance_comparison.html'


class TrialBalanceExportView(LoginRequiredMixin, SessionEntityMixin, DetailView):
    """
    Export trial balance as CSV
    """
    model = TrialBalance
    
    def render_to_response(self, context, **response_kwargs):
        tb = self.object
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="trial_balance_{tb.as_of_date}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Trial Balance', tb.as_of_date])
        writer.writerow([])
        writer.writerow(['Account Code', 'Account Name', 'Debit', 'Credit', 'Balance'])
        writer.writerow([])
        writer.writerow(['TOTALS', '', tb.total_debits, tb.total_credits, ''])
        
        return response


class TrialBalanceDashboardView(LoginRequiredMixin, SessionEntityMixin, TemplateView):
    """
    Trial Balance Dashboard - summary and quick actions
    """
    template_name = 'accounting/trial_balance_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get latest trial balance
        latest_tb = TrialBalance.objects.filter(entity=self.entity).order_by('-as_of_date').first()
        
        # Get counts
        total_tb_count = TrialBalance.objects.filter(entity=self.entity).count()
        balanced_count = TrialBalance.objects.filter(entity=self.entity, is_balanced=True).count()
        unbalanced_count = total_tb_count - balanced_count
        
        context['latest_tb'] = latest_tb
        context['total_count'] = total_tb_count
        context['balanced_count'] = balanced_count
        context['unbalanced_count'] = unbalanced_count
        
        return context


class MonthlyTrialBalanceListView(LoginRequiredMixin, SessionEntityMixin, ListView):
    """
    List monthly trial balance archives
    """
    model = TrialBalance
    template_name = 'accounting/monthly_trial_balance_list.html'
    context_object_name = 'monthly_tbs'
    paginate_by = 20
    
    def get_queryset(self):
        return TrialBalance.objects.filter(
            entity=self.entity
        ).order_by('-as_of_date')
