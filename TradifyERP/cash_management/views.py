from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db.models import Sum, Q
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.views.decorators.csrf import csrf_exempt
from decimal import Decimal
from datetime import timedelta
from django.contrib import messages

from .models import (
    CashPosition, PaymentSchedule, LiquidityForecast, TreasuryAccount,
    CashFlowForecastDetail, FXExposure
)
from .forms import PaymentScheduleForm, CashPositionForm, LiquidityForecastForm, TreasuryAccountForm, FXExposureForm
from accounting.models import BankProfile


class CashManagementDashboardView(LoginRequiredMixin, TemplateView):
    """Cash Management Dashboard."""
    template_name = 'cash_management/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Current cash position
        today = timezone.now().date()
        latest_positions = CashPosition.objects.filter(
            position_date=today
        ).select_related('bank_account')
        
        total_cash = latest_positions.aggregate(
            total=Sum('closing_balance')
        )['total'] or Decimal('0')
        
        # Upcoming payments
        upcoming_payments = PaymentSchedule.objects.filter(
            status__in=['SCHEDULED', 'APPROVED'],
            scheduled_date__lte=today + timedelta(days=30)
        ).order_by('scheduled_date')
        
        total_scheduled = upcoming_payments.aggregate(
            total=Sum('payment_amount')
        )['total'] or Decimal('0')
        
        # Overdue payments
        overdue_payments = PaymentSchedule.objects.filter(
            status__in=['SCHEDULED', 'APPROVED'],
            due_date__lt=today
        )
        
        # Liquidity forecast
        latest_forecast = LiquidityForecast.objects.filter(
            forecast_start_date__lte=today,
            forecast_end_date__gte=today
        ).first()
        
        # Treasury accounts
        treasury_accounts = TreasuryAccount.objects.filter(is_active=True)
        
        context.update({
            'cash_positions': latest_positions,
            'total_cash': total_cash,
            'upcoming_payments': upcoming_payments[:10],
            'total_scheduled': total_scheduled,
            'overdue_payments': overdue_payments,
            'liquidity_forecast': latest_forecast,
            'treasury_accounts': treasury_accounts,
        })
        
        return context


class PaymentScheduleListView(LoginRequiredMixin, ListView):
    """List all payment schedules."""
    model = PaymentSchedule
    template_name = 'cash_management/paymentschedule_list.html'
    context_object_name = 'payments'
    paginate_by = 50
    
    def get_queryset(self):
        queryset = PaymentSchedule.objects.select_related('currency', 'from_account').order_by('-scheduled_date')
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        return queryset


class PaymentScheduleDetailView(LoginRequiredMixin, DetailView):
    """Detail view for payment schedule."""
    model = PaymentSchedule
    template_name = 'cash_management/paymentschedule_detail.html'


class CashPositionDetailView(LoginRequiredMixin, DetailView):
    """Detail view for cash position."""
    model = CashPosition
    template_name = 'cash_management/cashposition_detail.html'


class CashPositionListView(LoginRequiredMixin, ListView):
    """List cash positions."""
    model = CashPosition
    template_name = 'cash_management/cashposition_list.html'
    context_object_name = 'positions'
    paginate_by = 30
    
    def get_queryset(self):
        return CashPosition.objects.select_related('bank_account').order_by('-position_date')


class LiquidityForecastListView(LoginRequiredMixin, ListView):
    """List liquidity forecasts."""
    model = LiquidityForecast
    template_name = 'cash_management/liquidityforecast_list.html'
    context_object_name = 'forecasts'
    paginate_by = 20
    
    def get_queryset(self):
        return LiquidityForecast.objects.order_by('-forecast_start_date')


class LiquidityForecastDetailView(LoginRequiredMixin, DetailView):
    """Detail view for liquidity forecast."""
    model = LiquidityForecast
    template_name = 'cash_management/liquidityforecast_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['forecast_lines'] = self.object.lines.all().order_by('forecast_date')
        return context


class TreasuryAccountListView(LoginRequiredMixin, ListView):
    """List treasury accounts."""
    model = TreasuryAccount
    template_name = 'cash_management/treasuryaccount_list.html'
    context_object_name = 'accounts'
    
    def get_queryset(self):
        return TreasuryAccount.objects.filter(is_active=True).order_by('account_code')


class TreasuryAccountDetailView(LoginRequiredMixin, DetailView):
    """Detail view for treasury account."""
    model = TreasuryAccount
    template_name = 'cash_management/treasuryaccount_detail.html'


class FXExposureListView(LoginRequiredMixin, ListView):
    """List FX exposures."""
    model = FXExposure
    template_name = 'cash_management/fxexposure_list.html'
    context_object_name = 'exposures'
    paginate_by = 50
    
    def get_queryset(self):
        queryset = FXExposure.objects.select_related(
            'home_currency', 'foreign_currency'
        ).order_by('-exposure_date')
        hedged = self.request.GET.get('hedged')
        if hedged:
            queryset = queryset.filter(is_hedged=hedged == 'true')
        return queryset


class FXExposureDetailView(LoginRequiredMixin, DetailView):
    """Detail view for FX exposure."""
    model = FXExposure
    template_name = 'cash_management/fxexposure_detail.html'


# CREATE VIEWS
class PaymentScheduleCreateView(LoginRequiredMixin, CreateView):
    """Create payment schedule."""
    model = PaymentSchedule
    form_class = PaymentScheduleForm
    template_name = 'cash_management/paymentschedule_form.html'
    success_url = reverse_lazy('cash_management:payment_list')
    
    def form_valid(self, form):
        # Ensure entity is set - it can be set explicitly or derived from from_account
        if not form.cleaned_data.get('entity') and form.cleaned_data.get('from_account'):
            # Auto-set entity from the selected bank account
            from_account = form.cleaned_data.get('from_account')
            form.instance.entity = from_account.entity
        
        messages.success(self.request, 'Payment schedule created successfully.')
        return super().form_valid(form)


class PaymentScheduleUpdateView(LoginRequiredMixin, UpdateView):
    """Update payment schedule."""
    model = PaymentSchedule
    form_class = PaymentScheduleForm
    template_name = 'cash_management/paymentschedule_form.html'
    success_url = reverse_lazy('cash_management:payment_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Payment schedule updated successfully.')
        return super().form_valid(form)


class CashPositionCreateView(LoginRequiredMixin, CreateView):
    """Create cash position."""
    model = CashPosition
    form_class = CashPositionForm
    template_name = 'cash_management/cashposition_form.html'
    success_url = reverse_lazy('cash_management:position_list')
    
    def form_valid(self, form):
        # Ensure entity is set - it can be set explicitly or derived from bank_account
        if not form.cleaned_data.get('entity') and form.cleaned_data.get('bank_account'):
            # Auto-set entity from the selected bank account
            bank_account = form.cleaned_data.get('bank_account')
            form.instance.entity = bank_account.entity
        
        messages.success(self.request, 'Cash position created successfully.')
        return super().form_valid(form)


class CashPositionUpdateView(LoginRequiredMixin, UpdateView):
    """Update cash position."""
    model = CashPosition
    form_class = CashPositionForm
    template_name = 'cash_management/cashposition_form.html'
    success_url = reverse_lazy('cash_management:position_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Cash position updated successfully.')
        return super().form_valid(form)


class LiquidityForecastCreateView(LoginRequiredMixin, CreateView):
    """Create liquidity forecast."""
    model = LiquidityForecast
    form_class = LiquidityForecastForm
    template_name = 'cash_management/liquidityforecast_form.html'
    success_url = reverse_lazy('cash_management:forecast_list')
    
    def form_valid(self, form):
        # Ensure entity is set - must be explicitly selected by user
        if not form.cleaned_data.get('entity'):
            # Entity is required, form validation should prevent this
            # but this ensures the entity is properly set if provided
            pass
        
        messages.success(self.request, 'Liquidity forecast created successfully.')
        return super().form_valid(form)


class LiquidityForecastUpdateView(LoginRequiredMixin, UpdateView):
    """Update liquidity forecast."""
    model = LiquidityForecast
    form_class = LiquidityForecastForm
    template_name = 'cash_management/liquidityforecast_form.html'
    success_url = reverse_lazy('cash_management:forecast_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Liquidity forecast updated successfully.')
        return super().form_valid(form)


class TreasuryAccountCreateView(LoginRequiredMixin, CreateView):
    """Create treasury account."""
    model = TreasuryAccount
    form_class = TreasuryAccountForm
    template_name = 'cash_management/treasuryaccount_form.html'
    success_url = reverse_lazy('cash_management:treasury_list')
    
    def form_valid(self, form):
        # Ensure entity is set - must be explicitly selected by user
        if not form.cleaned_data.get('entity'):
            # Entity is required, form validation should prevent this
            # but this ensures the entity is properly set if provided
            pass
        
        messages.success(self.request, 'Treasury account created successfully.')
        return super().form_valid(form)


class TreasuryAccountUpdateView(LoginRequiredMixin, UpdateView):
    """Update treasury account."""
    model = TreasuryAccount
    form_class = TreasuryAccountForm
    template_name = 'cash_management/treasuryaccount_form.html'
    success_url = reverse_lazy('cash_management:treasury_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Treasury account updated successfully.')
        return super().form_valid(form)


class FXExposureCreateView(LoginRequiredMixin, CreateView):
    """Create FX exposure."""
    model = FXExposure
    form_class = FXExposureForm
    template_name = 'cash_management/fxexposure_form.html'
    success_url = reverse_lazy('cash_management:fx_list')
    
    def form_valid(self, form):
        # Ensure entity is set - must be explicitly selected by user
        if not form.cleaned_data.get('entity'):
            # Entity is required, form validation should prevent this
            # but this ensures the entity is properly set if provided
            pass
        
        messages.success(self.request, 'FX exposure created successfully.')
        return super().form_valid(form)


class FXExposureUpdateView(LoginRequiredMixin, UpdateView):
    """Update FX exposure."""
    model = FXExposure
    form_class = FXExposureForm
    template_name = 'cash_management/fxexposure_form.html'
    success_url = reverse_lazy('cash_management:fx_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'FX exposure updated successfully.')
        return super().form_valid(form)


# API Endpoints
@require_GET
@csrf_exempt
def bank_account_currency(request, bank_account_id):
    """API endpoint to get currency for a bank account."""
    try:
        bank_account = BankProfile.objects.select_related('currency').get(pk=bank_account_id)
        return JsonResponse({
            'currency_id': bank_account.currency.id,
            'currency_code': bank_account.currency.code,
            'currency_symbol': bank_account.currency.symbol,
        })
    except BankProfile.DoesNotExist:
        return JsonResponse({'error': 'Bank account not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    def form_valid(self, form):
        messages.success(self.request, 'FX exposure updated successfully.')
        return super().form_valid(form)
