"""
Trading & Manufacturing Account View
"""

from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django import forms
from datetime import datetime

from accounting.models import Entity
from accounting.trading_manufacturing import calculate_trading_manufacturing_account


class TradingManufacturingForm(forms.Form):
    """Form to select date range for Trading & Manufacturing Account."""
    
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


class TradingManufacturingAccountView(LoginRequiredMixin, TemplateView):
    """Display Trading & Manufacturing Account report."""
    template_name = 'accounting/trading_manufacturing_account.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get entity from session
        entity_id = self.request.session.get('selected_entity_id')
        entity = None
        if entity_id:
            entity = Entity.objects.filter(id=entity_id, is_active=True).first()
        
        # Get default entity if none selected
        if not entity:
            entity = Entity.objects.filter(is_active=True).first()
        
        if not entity:
            context['error'] = 'No entity found. Please create an entity first.'
            context['form'] = TradingManufacturingForm()
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
        
        # Calculate Trading & Manufacturing Account
        tm_data = calculate_trading_manufacturing_account(entity, period_start, period_end)
        
        # Create form with current values
        form = TradingManufacturingForm(initial={
            'period_start': period_start,
            'period_end': period_end
        })
        
        context.update({
            'entity': entity,
            'period_start': period_start,
            'period_end': period_end,
            'tm_data': tm_data,
            'form': form,
        })
        
        return context
    
    def post(self, request, *args, **kwargs):
        """Handle form submission to update date range."""
        from django.shortcuts import redirect
        
        form = TradingManufacturingForm(request.POST)
        if form.is_valid():
            period_start = form.cleaned_data['period_start']
            period_end = form.cleaned_data['period_end']
            
            # Redirect to same view with date parameters
            url = f'?period_start={period_start}&period_end={period_end}'
            return redirect('/accounting/trading-manufacturing/' + url)
        
        # If form invalid, reload page
        return redirect('/accounting/trading-manufacturing/')
