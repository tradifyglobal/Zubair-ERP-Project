"""
Accounting Views - P&L Report Display
Shows P&L data calculated from GL entries with Sales module integration.
"""

from django.views.generic import TemplateView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django import forms
from django.urls import reverse_lazy
from datetime import datetime, timedelta
from decimal import Decimal
from django.utils import timezone

from accounting.models import Entity, Account
from accounting.mixins import SessionEntityMixin
from accounting.pl_generator import (
    calculate_pl_from_gl,
    generate_pl_report,
    get_sales_revenue_for_period,
    get_tax_summary_for_period,
    get_ar_balance_for_period,
    get_pl_comparison
)


class ProfitLossReportForm(forms.Form):
    """Form to select date range for P&L report."""
    
    period_start = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
        }),
        label='Period Start'
    )
    
    period_end = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
        }),
        label='Period End'
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set default dates to current month
        today = datetime.now().date()
        self.fields['period_start'].initial = today.replace(day=1)
        self.fields['period_end'].initial = today


class ProfitLossDetailView(SessionEntityMixin, LoginRequiredMixin, FormView):
    """Display detailed P&L report with GL data."""
    template_name = 'accounting/profit_loss_detail.html'
    form_class = ProfitLossReportForm
    success_url = reverse_lazy('accounting:profit_loss_detail')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        entity_id = self.request.session.get('selected_entity_id')
        entity = Entity.objects.filter(id=entity_id, is_active=True).first()
        
        if not entity:
            return context
        
        # Get date range from GET params or form
        period_start = self.request.GET.get('period_start')
        period_end = self.request.GET.get('period_end')
        
        if period_start and period_end:
            try:
                period_start = datetime.strptime(period_start, '%Y-%m-%d').date()
                period_end = datetime.strptime(period_end, '%Y-%m-%d').date()
            except:
                # Invalid dates, use current month
                today = datetime.now().date()
                period_start = today.replace(day=1)
                period_end = today
        else:
            # Default to current month
            today = datetime.now().date()
            period_start = today.replace(day=1)
            period_end = today
        
        # Calculate P&L from GL
        pl_data = calculate_pl_from_gl(entity, period_start, period_end)
        
        # Get additional metrics
        sales_revenue = get_sales_revenue_for_period(entity, period_start, period_end)
        tax_summary = get_tax_summary_for_period(entity, period_start, period_end)
        ar_balance = get_ar_balance_for_period(entity, period_end, period_end)
        
        context.update({
            'entity': entity,
            'period_start': period_start,
            'period_end': period_end,
            'pl_data': pl_data,
            'sales_revenue': sales_revenue,
            'tax_summary': tax_summary,
            'ar_balance': ar_balance,
            'has_data': len(pl_data.get('lines', {}).get('revenue', [])) > 0 or len(pl_data.get('lines', {}).get('expenses', [])) > 0,
        })
        
        return context
    
    def post(self, request, *args, **kwargs):
        """Handle form submission to update date range."""
        form = self.get_form()
        if form.is_valid():
            period_start = form.cleaned_data['period_start']
            period_end = form.cleaned_data['period_end']
            
            # Redirect to same view with date parameters
            from django.http import redirect
            return redirect(
                f"{self.request.path}?period_start={period_start}&period_end={period_end}"
            )
        
        return self.form_invalid(form)


class ProfitLossComparisonView(SessionEntityMixin, LoginRequiredMixin, TemplateView):
    """Compare P&L across multiple periods."""
    template_name = 'accounting/profit_loss_comparison.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        entity_id = self.request.session.get('selected_entity_id')
        entity = Entity.objects.filter(id=entity_id, is_active=True).first()
        
        if not entity:
            return context
        
        # Get last 12 months for comparison
        today = datetime.now().date()
        periods = []
        
        for i in range(12):
            # Go back i months
            month = today.month - i
            year = today.year
            
            if month <= 0:
                month += 12
                year -= 1
            
            # Get first and last day of month
            if month == 12:
                next_month = datetime(year + 1, 1, 1).date()
            else:
                next_month = datetime(year, month + 1, 1).date()
            
            period_end = next_month - timedelta(days=1)
            period_start = datetime(year, month, 1).date()
            
            periods.append((period_start, period_end))
        
        # Reverse to show chronologically
        periods = list(reversed(periods))
        
        # Get comparison data
        comparison_data = get_pl_comparison(entity, periods)
        
        context.update({
            'entity': entity,
            'comparison_data': comparison_data,
            'has_data': len(comparison_data) > 0,
        })
        
        return context
