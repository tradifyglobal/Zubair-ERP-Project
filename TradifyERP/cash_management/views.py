from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db.models import Sum, Q
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta

from .models import (
    CashPosition, PaymentSchedule, LiquidityForecast, TreasuryAccount,
    CashFlowForecastDetail, FXExposure
)


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
