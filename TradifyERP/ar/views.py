from django.shortcuts import render
from django.views.generic import ListView, DetailView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, Q, Count
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from .models import CustomerInvoice, CustomerPayment, ARAging


class ARDashboardView(LoginRequiredMixin, TemplateView):
    """AR Dashboard with KPIs."""
    template_name = 'ar/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        today = timezone.now().date()
        
        # Invoice metrics
        total_invoices = CustomerInvoice.objects.filter(
            status__in=['ISSUED', 'SENT', 'PARTIALLY_PAID', 'PAID']
        ).count()
        
        total_outstanding = CustomerInvoice.objects.filter(
            status__in=['ISSUED', 'SENT', 'PARTIALLY_PAID']
        ).aggregate(total=Sum('total_amount') - Sum('amount_paid'))['total'] or Decimal('0')
        
        overdue_invoices = CustomerInvoice.objects.filter(
            status__in=['ISSUED', 'SENT', 'PARTIALLY_PAID'],
            due_date__lt=today
        )
        overdue_count = overdue_invoices.count()
        overdue_amount = overdue_invoices.aggregate(
            total=Sum('total_amount') - Sum('amount_paid')
        )['total'] or Decimal('0')
        
        # Recent invoices
        recent_invoices = CustomerInvoice.objects.filter(
            status__in=['ISSUED', 'SENT', 'PARTIALLY_PAID', 'PAID']
        ).order_by('-invoice_date')[:10]
        
        # Recent payments
        recent_payments = CustomerPayment.objects.order_by('-payment_date')[:10]
        
        # DSO (Days Sales Outstanding)
        paid_invoices = CustomerInvoice.objects.filter(status='PAID', invoice_date__gte=today - timedelta(days=90))
        if paid_invoices.exists():
            total_paid = paid_invoices.aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
            dso = (total_paid / 90) if total_paid > 0 else 0
        else:
            dso = 0
        
        context.update({
            'total_outstanding': total_outstanding,
            'total_invoices': total_invoices,
            'overdue_count': overdue_count,
            'overdue_amount': overdue_amount,
            'recent_invoices': recent_invoices,
            'recent_payments': recent_payments,
            'dso': round(dso, 1),
        })
        
        return context


class CustomerInvoiceListView(LoginRequiredMixin, ListView):
    """List all customer invoices."""
    model = CustomerInvoice
    template_name = 'ar/customerinvoice_list.html'
    context_object_name = 'invoices'
    paginate_by = 50
    
    def get_queryset(self):
        queryset = CustomerInvoice.objects.select_related('customer', 'entity').order_by('-invoice_date')
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        return queryset


class CustomerInvoiceDetailView(LoginRequiredMixin, DetailView):
    """Detail view for customer invoice."""
    model = CustomerInvoice
    template_name = 'ar/customerinvoice_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['line_items'] = self.object.line_items.all()
        context['payments'] = self.object.reconciliations.all()
        return context


class CustomerPaymentListView(LoginRequiredMixin, ListView):
    """List all customer payments."""
    model = CustomerPayment
    template_name = 'ar/customerpayment_list.html'
    context_object_name = 'payments'
    paginate_by = 50
    
    def get_queryset(self):
        queryset = CustomerPayment.objects.select_related('customer', 'entity').order_by('-payment_date')
        method = self.request.GET.get('method')
        if method:
            queryset = queryset.filter(payment_method=method)
        return queryset


class CustomerPaymentDetailView(LoginRequiredMixin, DetailView):
    """Detail view for customer payment."""
    model = CustomerPayment
    template_name = 'ar/customerpayment_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reconciliations'] = self.object.reconciliations.all()
        return context


class ARAgingReportView(LoginRequiredMixin, TemplateView):
    """Generate AR aging report."""
    template_name = 'ar/ar_aging_report.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        today = timezone.now().date()
        
        # Get all unpaid invoices
        unpaid_invoices = CustomerInvoice.objects.filter(
            status__in=['ISSUED', 'SENT', 'PARTIALLY_PAID']
        ).select_related('customer')
        
        # Age buckets
        current = []
        days_30_60 = []
        days_60_90 = []
        days_90_plus = []
        
        for invoice in unpaid_invoices:
            days_outstanding = (today - invoice.invoice_date).days
            outstanding_amount = invoice.total_amount - invoice.amount_paid
            
            if days_outstanding <= 30:
                current.append({
                    'invoice': invoice,
                    'outstanding': outstanding_amount,
                    'days': days_outstanding
                })
            elif days_outstanding <= 60:
                days_30_60.append({
                    'invoice': invoice,
                    'outstanding': outstanding_amount,
                    'days': days_outstanding
                })
            elif days_outstanding <= 90:
                days_60_90.append({
                    'invoice': invoice,
                    'outstanding': outstanding_amount,
                    'days': days_outstanding
                })
            else:
                days_90_plus.append({
                    'invoice': invoice,
                    'outstanding': outstanding_amount,
                    'days': days_outstanding
                })
        
        context.update({
            'current': current,
            'days_30_60': days_30_60,
            'days_60_90': days_60_90,
            'days_90_plus': days_90_plus,
            'total_current': sum(i['outstanding'] for i in current),
            'total_30_60': sum(i['outstanding'] for i in days_30_60),
            'total_60_90': sum(i['outstanding'] for i in days_60_90),
            'total_90_plus': sum(i['outstanding'] for i in days_90_plus),
            'as_of_date': today,
        })
        
        return context
