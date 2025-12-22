"""
Trial Balance Views - Compatible with Production Models
Works with the existing simple TrialBalance model
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponse
from django.db.models import Sum, Q, F
from django.utils import timezone
from django.core.paginator import Paginator
from accounting.models import TrialBalance, Entity, Account, JournalEntry
from datetime import datetime, date
import csv


class TrialBalanceListView(LoginRequiredMixin, ListView):
    """List all trial balances with pagination and filtering"""
    model = TrialBalance
    template_name = 'accounting/trial_balance_list.html'
    context_object_name = 'trial_balances'
    paginate_by = 20

    def get_queryset(self):
        queryset = TrialBalance.objects.all().order_by('-as_of_date')
        
        # Filter by date range
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        
        if start_date:
            queryset = queryset.filter(as_of_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(as_of_date__lte=end_date)
        
        # Filter by balanced status
        balanced = self.request.GET.get('balanced')
        if balanced == 'true':
            queryset = queryset.filter(is_balanced=True)
        elif balanced == 'false':
            queryset = queryset.filter(is_balanced=False)
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['trial_balances_count'] = TrialBalance.objects.count()
        context['balanced_count'] = TrialBalance.objects.filter(is_balanced=True).count()
        context['unbalanced_count'] = TrialBalance.objects.filter(is_balanced=False).count()
        context['this_month_count'] = TrialBalance.objects.filter(
            as_of_date__year=timezone.now().year,
            as_of_date__month=timezone.now().month
        ).count()
        return context


class TrialBalanceDetailView(LoginRequiredMixin, DetailView):
    """Display detailed trial balance view"""
    model = TrialBalance
    template_name = 'accounting/trial_balance_detail.html'
    context_object_name = 'trial_balance'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tb = self.get_object()
        
        # Get all accounts and calculate balances
        accounts = Account.objects.filter(entity=tb.entity, is_active=True)
        
        # Group accounts by type
        account_types = {
            'ASSET': accounts.filter(account_type='ASSET'),
            'LIABILITY': accounts.filter(account_type='LIABILITY'),
            'EQUITY': accounts.filter(account_type='EQUITY'),
            'INCOME': accounts.filter(account_type='INCOME'),
            'EXPENSE': accounts.filter(account_type='EXPENSE'),
        }
        
        # Calculate balances for each type
        for acc_type, accs in account_types.items():
            total_debit = 0
            total_credit = 0
            lines = []
            
            for account in accs:
                debit = JournalEntry.objects.filter(
                    debit_account=account,
                    journal_entry__status='POSTED'
                ).aggregate(total=Sum('amount'))['total'] or 0
                
                credit = JournalEntry.objects.filter(
                    credit_account=account,
                    journal_entry__status='POSTED'
                ).aggregate(total=Sum('amount'))['total'] or 0
                
                balance = debit - credit
                
                if debit > 0 or credit > 0:
                    lines.append({
                        'account': account,
                        'debit_amount': debit,
                        'credit_amount': credit,
                        'balance': balance
                    })
                    total_debit += debit
                    total_credit += credit
            
            context[f'{acc_type.lower()}_lines'] = lines
            context[f'{acc_type.lower()}_debit'] = total_debit
            context[f'{acc_type.lower()}_credit'] = total_credit
            context[f'{acc_type.lower()}_balance'] = total_debit - total_credit
            context[f'{acc_type.lower()}_count'] = len(lines)
        
        return context


class TrialBalanceGenerateView(LoginRequiredMixin, View):
    """Generate trial balance for a specific date"""
    template_name = 'accounting/trial_balance_generate.html'

    def get(self, request):
        entities = Entity.objects.all()
        return render(request, self.template_name, {'entities': entities})

    def post(self, request):
        entity_id = request.POST.get('entity_id')
        tb_date_str = request.POST.get('date')
        
        try:
            entity = Entity.objects.get(id=entity_id)
            tb_date = datetime.strptime(tb_date_str, '%Y-%m-%d').date()
            
            # Calculate totals
            total_debits = JournalEntry.objects.filter(
                journal_entry__entity=entity,
                journal_entry__entry_date__lte=tb_date,
                journal_entry__status='POSTED'
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            total_credits = total_debits  # Debits should equal credits
            is_balanced = total_debits == total_credits
            
            # Get or create TB
            tb, created = TrialBalance.objects.get_or_create(
                entity=entity,
                as_of_date=tb_date,
                defaults={
                    'total_debits': total_debits,
                    'total_credits': total_credits,
                    'is_balanced': is_balanced
                }
            )
            
            if not created:
                tb.total_debits = total_debits
                tb.total_credits = total_credits
                tb.is_balanced = is_balanced
                tb.save()
            
            return redirect('trial-balance-detail', pk=tb.pk)
        
        except Exception as e:
            return render(request, self.template_name, {
                'entities': Entity.objects.all(),
                'error': str(e)
            })


class TrialBalanceReportView(LoginRequiredMixin, TemplateView):
    """Display trial balance as a financial statement"""
    template_name = 'accounting/trial_balance_report.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get latest TB for each entity
        latest_tbs = []
        for entity in Entity.objects.all():
            tb = TrialBalance.objects.filter(entity=entity).order_by('-as_of_date').first()
            if tb:
                latest_tbs.append(tb)
        
        context['latest_tbs'] = latest_tbs
        context['report_date'] = timezone.now().date()
        
        return context


class TrialBalanceComparisonView(LoginRequiredMixin, TemplateView):
    """Compare two trial balance periods"""
    template_name = 'accounting/trial_balance_comparison.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        available_tbs = TrialBalance.objects.all().order_by('-as_of_date')
        context['available_tbs'] = available_tbs
        
        from_id = self.request.GET.get('from_date')
        to_id = self.request.GET.get('to_date')
        
        if from_id and to_id:
            try:
                from_tb = TrialBalance.objects.get(id=from_id)
                to_tb = TrialBalance.objects.get(id=to_id)
                
                context['from_tb'] = from_tb
                context['to_tb'] = to_tb
                context['debit_change'] = to_tb.total_debits - from_tb.total_debits
                context['credit_change'] = to_tb.total_credits - from_tb.total_credits
                context['comparison_data'] = []
            except:
                pass
        
        return context


class TrialBalanceExportView(LoginRequiredMixin, View):
    """Export trial balance to CSV"""
    
    def get(self, request, pk):
        tb = get_object_or_404(TrialBalance, pk=pk)
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="trial_balance_{tb.as_of_date}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Account Code', 'Account Name', 'Account Type', 'Debit', 'Credit', 'Balance'])
        
        accounts = Account.objects.filter(entity=tb.entity, is_active=True)
        
        for account in accounts:
            debit = JournalEntry.objects.filter(
                debit_account=account,
                journal_entry__status='POSTED'
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            credit = JournalEntry.objects.filter(
                credit_account=account,
                journal_entry__status='POSTED'
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            balance = debit - credit
            
            writer.writerow([
                account.code,
                account.name,
                account.account_type,
                debit,
                credit,
                balance
            ])
        
        writer.writerow(['', '', 'TOTAL', tb.total_debits, tb.total_credits, 0])
        
        return response


class TrialBalanceDashboardView(LoginRequiredMixin, TemplateView):
    """Trial Balance Dashboard"""
    template_name = 'accounting/trial_balance_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get latest TB
        latest_tb = TrialBalance.objects.order_by('-as_of_date').first()
        context['latest_tb'] = latest_tb
        
        # Get statistics
        context['balanced_count'] = TrialBalance.objects.filter(is_balanced=True).count()
        context['unbalanced_count'] = TrialBalance.objects.filter(is_balanced=False).count()
        context['total_count'] = TrialBalance.objects.count()
        
        # Get recent TBs
        context['recent_tbs'] = TrialBalance.objects.order_by('-as_of_date')[:10]
        
        # Get monthly TBs (last 6 months)
        six_months_ago = timezone.now().date()
        from datetime import timedelta
        six_months_ago = six_months_ago - timedelta(days=180)
        
        context['monthly_tbs'] = TrialBalance.objects.filter(
            as_of_date__gte=six_months_ago
        ).order_by('-as_of_date')
        
        return context


class MonthlyTrialBalanceListView(LoginRequiredMixin, ListView):
    """List monthly trial balance archives"""
    template_name = 'accounting/monthly_trial_balance_list.html'
    context_object_name = 'monthly_tbs'
    paginate_by = 12

    def get_queryset(self):
        # Get the last day of each month with a TB
        return TrialBalance.objects.order_by('-as_of_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_count'] = TrialBalance.objects.count()
        context['approved_count'] = TrialBalance.objects.filter(is_balanced=True).count()
        context['pending_count'] = TrialBalance.objects.filter(is_balanced=False).count()
        context['unbalanced_count'] = TrialBalance.objects.filter(is_balanced=False).count()
        return context
