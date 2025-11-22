from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db.models import Q, Sum, F
from django.utils import timezone
from datetime import timedelta

from .models import VendorBill, VendorPayment, APAging, VendorBillLineItem
from .forms import (
    VendorBillForm, VendorBillLineItemForm, VendorPaymentForm, 
    APDiscountForm, APReconciliationForm
)


class APDashboardView(LoginRequiredMixin, TemplateView):
    """AP Module Dashboard - overview of bills, payments, and aging."""
    template_name = 'ap/dashboard.html'
    login_url = 'login'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get bills by status
        bills_total = VendorBill.objects.count()
        bills_posted = VendorBill.objects.filter(status='POSTED').count()
        bills_unpaid = VendorBill.objects.filter(payment_status='UNPAID').count()
        bills_overdue = VendorBill.objects.filter(due_date__lt=timezone.now(), payment_status='UNPAID').count()
        
        # Outstanding payables
        outstanding = VendorBill.objects.filter(
            payment_status__in=['UNPAID', 'PARTIAL']
        ).aggregate(total=Sum('total_amount') - Sum('amount_paid'))['total'] or 0
        
        # Recent bills
        recent_bills = VendorBill.objects.order_by('-bill_date')[:10]
        
        # Recent payments
        recent_payments = VendorPayment.objects.order_by('-payment_date')[:10]
        
        context.update({
            'bills_total': bills_total,
            'bills_posted': bills_posted,
            'bills_unpaid': bills_unpaid,
            'bills_overdue': bills_overdue,
            'outstanding_payables': outstanding,
            'recent_bills': recent_bills,
            'recent_payments': recent_payments,
        })
        
        return context


class VendorBillListView(LoginRequiredMixin, ListView):
    """List all vendor bills with filtering and search."""
    model = VendorBill
    template_name = 'ap/vendorbill_list.html'
    context_object_name = 'bills'
    paginate_by = 20
    login_url = 'login'
    
    def get_queryset(self):
        queryset = VendorBill.objects.all().select_related('vendor', 'entity').order_by('-bill_date')
        
        # Search by bill number or vendor name
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(bill_number__icontains=search) | 
                Q(vendor__name__icontains=search)
            )
        
        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Filter by payment status
        payment_status = self.request.GET.get('payment_status')
        if payment_status:
            queryset = queryset.filter(payment_status=payment_status)
        
        # Filter by entity
        entity = self.request.GET.get('entity')
        if entity:
            queryset = queryset.filter(entity_id=entity)
        
        return queryset


class VendorBillDetailView(LoginRequiredMixin, DetailView):
    """Display detailed view of a vendor bill with line items."""
    model = VendorBill
    template_name = 'ap/vendorbill_detail.html'
    context_object_name = 'bill'
    login_url = 'login'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        bill = self.get_object()
        context['line_items'] = bill.vendorbilllineitem_set.all()
        context['payments'] = bill.ap_vendor_payments.all()
        return context


class VendorBillCreateView(LoginRequiredMixin, CreateView):
    """Create a new vendor bill."""
    model = VendorBill
    form_class = VendorBillForm
    template_name = 'ap/vendorbill_form.html'
    success_url = reverse_lazy('ap:bill_list')
    login_url = 'login'
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class VendorBillUpdateView(LoginRequiredMixin, UpdateView):
    """Update an existing vendor bill."""
    model = VendorBill
    form_class = VendorBillForm
    template_name = 'ap/vendorbill_form.html'
    success_url = reverse_lazy('ap:bill_list')
    login_url = 'login'


class VendorBillApproveView(LoginRequiredMixin, UpdateView):
    """Approve a vendor bill."""
    model = VendorBill
    fields = []
    template_name = 'ap/vendorbill_confirm_approve.html'
    success_url = reverse_lazy('ap:bill_list')
    login_url = 'login'
    
    def form_valid(self, form):
        form.instance.is_approved = True
        form.instance.approved_by = self.request.user
        return super().form_valid(form)


class VendorBillPostView(LoginRequiredMixin, UpdateView):
    """Post a vendor bill to GL (creates GL entries)."""
    model = VendorBill
    fields = []
    template_name = 'ap/vendorbill_confirm_post.html'
    success_url = reverse_lazy('ap:bill_list')
    login_url = 'login'
    
    def form_valid(self, form):
        from accounting.models import LedgerEntry, Account
        
        bill = self.get_object()
        if not bill.is_approved:
            form.add_error(None, 'Bill must be approved before posting.')
            return self.form_invalid(form)
        
        # TODO: Implement GL posting logic
        # Create debit to expense account, credit to AP account
        bill.status = 'POSTED'
        return super().form_valid(form)


class VendorPaymentListView(LoginRequiredMixin, ListView):
    """List all vendor payments with filtering and search."""
    model = VendorPayment
    template_name = 'ap/vendorpayment_list.html'
    context_object_name = 'payments'
    paginate_by = 20
    login_url = 'login'
    
    def get_queryset(self):
        queryset = VendorPayment.objects.all().select_related('vendor', 'entity').order_by('-payment_date')
        
        # Search by payment number or vendor name
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(payment_number__icontains=search) | 
                Q(vendor__name__icontains=search)
            )
        
        # Filter by payment method
        payment_method = self.request.GET.get('payment_method')
        if payment_method:
            queryset = queryset.filter(payment_method=payment_method)
        
        # Filter by entity
        entity = self.request.GET.get('entity')
        if entity:
            queryset = queryset.filter(entity_id=entity)
        
        return queryset


class VendorPaymentDetailView(LoginRequiredMixin, DetailView):
    """Display detailed view of a vendor payment."""
    model = VendorPayment
    template_name = 'ap/vendorpayment_detail.html'
    context_object_name = 'payment'
    login_url = 'login'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        payment = self.get_object()
        context['bills'] = payment.bills.all()
        return context


class VendorPaymentCreateView(LoginRequiredMixin, CreateView):
    """Create a new vendor payment."""
    model = VendorPayment
    form_class = VendorPaymentForm
    template_name = 'ap/vendorpayment_form.html'
    success_url = reverse_lazy('ap:payment_list')
    login_url = 'login'
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class VendorPaymentUpdateView(LoginRequiredMixin, UpdateView):
    """Update an existing vendor payment."""
    model = VendorPayment
    form_class = VendorPaymentForm
    template_name = 'ap/vendorpayment_form.html'
    success_url = reverse_lazy('ap:payment_list')
    login_url = 'login'


class APAgingReportView(LoginRequiredMixin, TemplateView):
    """Generate AP Aging Report - summary of unpaid bills by age."""
    template_name = 'ap/aging_report.html'
    login_url = 'login'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        today = timezone.now().date()
        
        # Calculate aging buckets with counts
        current_bills = VendorBill.objects.filter(
            due_date__gte=today,
            payment_status__in=['UNPAID', 'PARTIAL']
        )
        current_amount = current_bills.aggregate(
            total=Sum(F('total_amount') - F('amount_paid'))
        )['total'] or 0
        current_count = current_bills.count()
        
        days_1_30_bills = VendorBill.objects.filter(
            due_date__gte=today - timedelta(days=30),
            due_date__lt=today,
            payment_status__in=['UNPAID', 'PARTIAL']
        )
        days_1_30 = days_1_30_bills.aggregate(
            total=Sum(F('total_amount') - F('amount_paid'))
        )['total'] or 0
        count_1_30 = days_1_30_bills.count()
        
        days_31_60_bills = VendorBill.objects.filter(
            due_date__gte=today - timedelta(days=60),
            due_date__lt=today - timedelta(days=30),
            payment_status__in=['UNPAID', 'PARTIAL']
        )
        days_31_60 = days_31_60_bills.aggregate(
            total=Sum(F('total_amount') - F('amount_paid'))
        )['total'] or 0
        count_31_60 = days_31_60_bills.count()
        
        days_61_90_bills = VendorBill.objects.filter(
            due_date__gte=today - timedelta(days=90),
            due_date__lt=today - timedelta(days=60),
            payment_status__in=['UNPAID', 'PARTIAL']
        )
        days_61_90 = days_61_90_bills.aggregate(
            total=Sum(F('total_amount') - F('amount_paid'))
        )['total'] or 0
        count_61_90 = days_61_90_bills.count()
        
        over_90_bills = VendorBill.objects.filter(
            due_date__lt=today - timedelta(days=90),
            payment_status__in=['UNPAID', 'PARTIAL']
        )
        over_90 = over_90_bills.aggregate(
            total=Sum(F('total_amount') - F('amount_paid'))
        )['total'] or 0
        count_over_90 = over_90_bills.count()
        
        total_amount = current_amount + days_1_30 + days_31_60 + days_61_90 + over_90
        total_count = current_count + count_1_30 + count_31_60 + count_61_90 + count_over_90
        
        # Get all outstanding bills for detailed report
        all_outstanding = VendorBill.objects.filter(
            payment_status__in=['UNPAID', 'PARTIAL']
        ).select_related('vendor').order_by('due_date')
        
        aging_records = []
        for bill in all_outstanding:
            days_past_due = (today - bill.due_date).days if bill.due_date < today else 0
            outstanding_amount = bill.total_amount - bill.amount_paid
            
            # Determine age bucket
            if bill.due_date >= today:
                age_bucket = 'Current'
            elif bill.due_date >= today - timedelta(days=30):
                age_bucket = '1-30 Days'
            elif bill.due_date >= today - timedelta(days=60):
                age_bucket = '31-60 Days'
            elif bill.due_date >= today - timedelta(days=90):
                age_bucket = '61-90 Days'
            else:
                age_bucket = 'Over 90 Days'
            
            aging_records.append({
                'bill': bill,
                'days_past_due': days_past_due,
                'outstanding_amount': outstanding_amount,
                'age_bucket': age_bucket,
            })
        
        # Vendor summary
        vendor_summaries = {}
        for bill in all_outstanding:
            vendor_name = bill.vendor.name
            if vendor_name not in vendor_summaries:
                vendor_summaries[vendor_name] = {
                    'vendor_name': vendor_name,
                    'bill_count': 0,
                    'total_amount': 0,
                    'amount_paid': 0,
                    'outstanding': 0,
                    'overdue_amount': 0,
                }
            
            summary = vendor_summaries[vendor_name]
            summary['bill_count'] += 1
            summary['total_amount'] += bill.total_amount
            summary['amount_paid'] += bill.amount_paid
            summary['outstanding'] += bill.total_amount - bill.amount_paid
            
            if bill.due_date < today:
                summary['overdue_amount'] += bill.total_amount - bill.amount_paid
        
        # Calculate overdue percentage
        vendor_list = []
        for vendor_name, summary in vendor_summaries.items():
            if summary['outstanding'] > 0:
                summary['overdue_percentage'] = round(
                    (summary['overdue_amount'] / summary['outstanding']) * 100
                )
            else:
                summary['overdue_percentage'] = 0
            vendor_list.append(summary)
        
        context.update({
            'current_amount': round(current_amount, 2),
            'current_count': current_count,
            'days_1_30': round(days_1_30, 2),
            'count_1_30': count_1_30,
            'days_31_60': round(days_31_60, 2),
            'count_31_60': count_31_60,
            'days_61_90': round(days_61_90, 2),
            'count_61_90': count_61_90,
            'over_90': round(over_90, 2),
            'count_over_90': count_over_90,
            'total_amount': round(total_amount, 2),
            'total_count': total_count,
            'aging_records': aging_records,
            'vendor_summaries': vendor_list,
            'as_of_date': today,
        })
        
        return context
