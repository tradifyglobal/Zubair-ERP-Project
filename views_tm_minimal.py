"""
Trading & Manufacturing Account View - Minimal Test Version
"""

from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from datetime import datetime


class TradingManufacturingAccountView(LoginRequiredMixin, TemplateView):
    """Display Trading & Manufacturing Account report."""
    template_name = 'accounting/trading_manufacturing_account.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Minimal context for testing
        today = datetime.now().date()
        
        context.update({
            'period_start': today.replace(day=1),
            'period_end': today,
            'tm_data': {
                'revenue_section': [],
                'cost_section': [],
                'total_sales': 0,
                'total_costs': 0,
                'gross_profit': 0,
                'gross_profit_percentage': 0,
            }
        })
        
        return context
