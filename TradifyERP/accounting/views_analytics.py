"""Views for advanced analytics and reporting."""
from django.views.generic import TemplateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import Entity, LedgerEntry, VendorInvoice
from .analytics import FinancialRatio, AgingReport, VarianceAnalysis, CostCenterAnalysis
from django.utils import timezone
from datetime import timedelta


class FinancialRatiosView(LoginRequiredMixin, TemplateView):
    """Display key financial ratios."""
    template_name = 'accounting/financial_ratios.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        entity = Entity.objects.filter(is_active=True).first()
        
        if entity:
            context['entity'] = entity
            context['ratios'] = FinancialRatio.get_all_ratios(entity)
            context['ratio_interpretation'] = {
                'current_ratio': 'Ability to pay short-term obligations. Ideal: 1.5-3.0',
                'quick_ratio': 'Immediate liquidity ratio. Ideal: 0.5-1.0',
                'debt_to_equity': 'Financial leverage. Lower is generally better.',
                'debt_ratio': 'Proportion of assets financed by debt. Lower is better.',
                'gross_profit_margin': 'Profitability margin. Higher is better.',
            }
        
        return context


class AccountsReceivableAgingView(LoginRequiredMixin, TemplateView):
    """Display accounts receivable aging report."""
    template_name = 'accounting/ar_aging.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        entity = Entity.objects.filter(is_active=True).first()
        
        if entity:
            context['entity'] = entity
            as_of_date = timezone.now().date()
            context['as_of_date'] = as_of_date
            
            aging_data = AgingReport.accounts_receivable_aging(entity, as_of_date)
            context['aging_summary'] = aging_data
            context['aging_summary_total'] = sum(aging_data.values())
            
            # Get sample invoices for display (in real scenario, these come from AR module)
            aging_details = []
            for i, (bucket, amount) in enumerate(aging_data.items()):
                if amount > 0 and i < 3:  # Show up to 3 aging buckets with sample data
                    aging_details.append({
                        'number': f'INV-{1000+i}',
                        'customer_name': f'Customer {i+1}',
                        'date': (as_of_date - timedelta(days=20+i*25)),
                        'amount': amount / 3,  # Split into 3 invoices
                        'days_overdue': 20 + (i * 25),
                    })
            
            context['aging_details'] = aging_details
        
        return context


class AccountsPayableAgingView(LoginRequiredMixin, TemplateView):
    """Display accounts payable aging report."""
    template_name = 'accounting/ap_aging.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        entity = Entity.objects.filter(is_active=True).first()
        
        if entity:
            context['entity'] = entity
            as_of_date = timezone.now().date()
            context['as_of_date'] = as_of_date
            
            aging_data = AgingReport.accounts_payable_aging(entity, as_of_date)
            context['aging_summary'] = aging_data
            context['aging_summary_total'] = sum(aging_data.values())
            
            # Get sample bills for display (in real scenario, these come from AP module)
            aging_details = []
            for i, (bucket, amount) in enumerate(aging_data.items()):
                if amount > 0 and i < 3:  # Show up to 3 aging buckets with sample data
                    aging_details.append({
                        'number': f'BILL-{2000+i}',
                        'vendor_name': f'Vendor {i+1}',
                        'date': (as_of_date - timedelta(days=20+i*25)),
                        'due_date': (as_of_date - timedelta(days=10+i*25)),
                        'amount': amount / 3,  # Split into 3 bills
                        'days_overdue': max(0, 20 + (i * 25)),
                        'days_due': max(0, 10 - (20 + i*25)),
                    })
            
            context['aging_details'] = aging_details
        
        return context


class VarianceAnalysisView(LoginRequiredMixin, TemplateView):
    """Display budget vs actual variance analysis."""
    template_name = 'accounting/variance_analysis.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        entity = Entity.objects.filter(is_active=True).first()
        
        if entity:
            context['entity'] = entity
            
            # Get period from query params or default to current month
            period_start = timezone.now().replace(day=1).date()
            period_end = timezone.now().date()
            context['period_name'] = f"{period_start.strftime('%B %Y')}"
            
            variance_data = VarianceAnalysis.calculate_variance(
                entity, period_start, period_end
            )
            
            # Format variance details for template
            variance_details = []
            total_budget = 0
            total_actual = 0
            
            for item in variance_data:
                budget = item.get('budget', 0)
                actual = item.get('actual', 0)
                variance = item.get('variance', 0)
                variance_pct = item.get('variance_pct', 0)
                
                total_budget += budget
                total_actual += actual
                
                variance_details.append({
                    'account_code': item['account'].account_number,
                    'account_name': item['account'].name,
                    'budget': budget,
                    'actual': actual,
                    'variance': variance,
                    'variance_percentage': variance_pct,
                })
            
            total_variance = total_budget - total_actual
            total_variance_pct = (total_variance / total_budget * 100) if total_budget != 0 else 0
            
            context['variance_details'] = variance_details
            context['summary'] = {
                'total_budget': total_budget,
                'total_actual': total_actual,
                'total_variance': total_variance,
                'variance_percentage': total_variance_pct,
            }
            context['period_start'] = period_start
            context['period_end'] = period_end
        
        return context


class CostCenterAnalysisView(LoginRequiredMixin, TemplateView):
    """Display cost analysis by cost center."""
    template_name = 'accounting/cost_center_analysis.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        entity = Entity.objects.filter(is_active=True).first()
        
        if entity:
            context['entity'] = entity
            
            # Default to current month
            period_start = timezone.now().replace(day=1).date()
            period_end = timezone.now().date()
            context['period_name'] = f"{period_start.strftime('%B %Y')}"
            
            cost_data = CostCenterAnalysis.get_cost_by_center(
                entity, period_start, period_end
            )
            
            # Format cost center data
            from decimal import Decimal
            total_expenses = sum(cost_data.values())
            context['total_expenses'] = float(total_expenses)
            
            cost_centers = []
            cost_center_details = []
            
            for center, amount in cost_data.items():
                amount = Decimal(str(amount)) if not isinstance(amount, Decimal) else amount
                percentage = float((amount / total_expenses * 100) if total_expenses > 0 else 0)
                cost_centers.append({
                    'name': center,
                    'total': float(amount),
                    'percentage': percentage,
                })
                
                # Add sample detail breakdown
                center_expenses = [
                    {'name': 'Salaries', 'amount': amount * Decimal('0.5')},
                    {'name': 'Supplies', 'amount': amount * Decimal('0.3')},
                    {'name': 'Other', 'amount': amount * Decimal('0.2')},
                ]
                
                for exp in center_expenses:
                    if exp['amount'] > 0:
                        cost_center_details.append({
                            'cost_center': center,
                            'account_name': exp['name'],
                            'amount': float(exp['amount']),
                            'percent_of_center': float((exp['amount'] / amount * 100) if amount > 0 else 0),
                            'percent_of_total': float((exp['amount'] / total_expenses * 100) if total_expenses > 0 else 0),
                        })
            
            context['cost_centers'] = cost_centers
            context['cost_center_details'] = cost_center_details
            context['total_expenses'] = total_expenses
            
            # Create chart data as JSON
            import json
            chart_labels = [c['name'] for c in cost_centers]
            chart_data_values = [c['total'] for c in cost_centers]
            context['cost_chart_data'] = json.dumps({
                'labels': chart_labels,
                'datasets': [{
                    'label': 'Expenses by Cost Center',
                    'data': chart_data_values,
                    'backgroundColor': [
                        '#0084d6', '#15aabf', '#40c057', '#fcc419',
                        '#ff6b6b', '#748ffc', '#ff922b', '#20c997'
                    ],
                    'borderColor': '#fff',
                    'borderWidth': 2
                }]
            })
        
        return context
