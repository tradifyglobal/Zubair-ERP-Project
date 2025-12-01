"""
Views for Cash Management Module
Handles CRUD operations for cash receipts, payments, bank receipts, and payments
"""
from django.shortcuts import redirect, get_object_or_404
from django.views.generic import CreateView, ListView, DetailView, UpdateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.contrib import messages
from datetime import datetime
from decimal import Decimal
from .models import (
    CashReceiptLine, CashPaymentLine, BankReceiptLine, BankPaymentLine,
    Account, LedgerEntry, AuditLog
)
from .cash_forms import (
    CashReceiptLineForm, CashPaymentLineForm, BankReceiptLineForm, BankPaymentLineForm
)
from .mixins import SessionEntityMixin


class CashReceiptCreateView(LoginRequiredMixin, SessionEntityMixin, CreateView):
    """Create new cash receipt transaction."""
    model = CashReceiptLine
    form_class = CashReceiptLineForm
    template_name = 'accounting/cash_receipt_form.html'
    success_url = reverse_lazy('accounting:cash_receipt_list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if not kwargs.get('data'):
            initial = kwargs.get('initial', {})
            initial['date'] = datetime.now().date()
            kwargs['initial'] = initial
        return kwargs
    
    def form_valid(self, form):
        """Process valid form and save as DRAFT without creating GL entries yet."""
        form.instance.entity = self.request.entity
        form.instance.workflow_status = 'DRAFT'
        form.instance.status = 'DRAFT'
        
        try:
            receipt = form.save()
            
            # Create audit log
            AuditLog.objects.create(
                user=self.request.user,
                action='create_cash_receipt',
                model_name='CashReceiptLine',
                object_id=receipt.id,
                entity=self.request.entity,
                description=f"Created cash receipt: {receipt.description}"
            )
            
            messages.success(self.request, f'Cash receipt created successfully! Status: Draft - Awaiting approval')
        except Exception as e:
            messages.error(self.request, f'Error saving cash receipt: {str(e)}')
            return self.form_invalid(form)
        
        return redirect('accounting:cash_receipt_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Create Cash Receipt'
        context['breadcrumb'] = [
            {'name': 'Dashboard', 'url': '/accounting/dashboard/'},
            {'name': 'Cash Management', 'url': '#'},
            {'name': 'Cash Receipts', 'url': 'cash_receipt_list'},
            {'name': 'New Receipt', 'url': '#'},
        ]
        return context


class CashReceiptListView(LoginRequiredMixin, SessionEntityMixin, ListView):
    """List all cash receipts for current entity."""
    model = CashReceiptLine
    template_name = 'accounting/cash_receipt_list.html'
    context_object_name = 'receipts'
    paginate_by = 50
    
    def get_queryset(self):
        entity_id = self.request.session.get('selected_entity_id')
        queryset = CashReceiptLine.objects.filter(entity_id=entity_id).order_by('-date')
        
        # Filter by status if provided
        status = self.request.GET.get('status')
        if status in ['DRAFT', 'POSTED']:
            queryset = queryset.filter(status=status)
        
        # Search by description or reference
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                description__icontains=search
            ) | queryset.filter(
                reference_number__icontains=search
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Cash Receipts'
        entity_id = self.request.session.get('selected_entity_id')
        context['status_counts'] = {
            'draft': CashReceiptLine.objects.filter(entity_id=entity_id, status='DRAFT').count(),
            'posted': CashReceiptLine.objects.filter(entity_id=entity_id, status='POSTED').count(),
        }
        return context


class CashPaymentCreateView(LoginRequiredMixin, SessionEntityMixin, CreateView):
    """Create new cash payment transaction."""
    model = CashPaymentLine
    form_class = CashPaymentLineForm
    template_name = 'accounting/cash_payment_form.html'
    success_url = reverse_lazy('accounting:cash_payment_list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if not kwargs.get('data'):
            initial = kwargs.get('initial', {})
            initial['date'] = datetime.now().date()
            kwargs['initial'] = initial
        return kwargs
    
    def form_valid(self, form):
        """Process valid form and save as DRAFT without creating GL entries yet."""
        form.instance.entity = self.request.entity
        form.instance.workflow_status = 'DRAFT'
        form.instance.status = 'DRAFT'
        
        try:
            payment = form.save()
            
            # Create audit log
            AuditLog.objects.create(
                user=self.request.user,
                action='create_cash_payment',
                model_name='CashPaymentLine',
                object_id=payment.id,
                entity=self.request.entity,
                description=f"Created cash payment: {payment.description}"
            )
            
            messages.success(self.request, f'Cash payment created successfully! Status: Draft - Awaiting approval')
        except Exception as e:
            messages.error(self.request, f'Error saving cash payment: {str(e)}')
            return self.form_invalid(form)
        
        return redirect('accounting:cash_payment_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Create Cash Payment'
        context['breadcrumb'] = [
            {'name': 'Dashboard', 'url': '/accounting/dashboard/'},
            {'name': 'Cash Management', 'url': '#'},
            {'name': 'Cash Payments', 'url': 'cash_payment_list'},
            {'name': 'New Payment', 'url': '#'},
        ]
        return context


class CashPaymentListView(LoginRequiredMixin, SessionEntityMixin, ListView):
    """List all cash payments for current entity."""
    model = CashPaymentLine
    template_name = 'accounting/cash_payment_list.html'
    context_object_name = 'payments'
    paginate_by = 50
    
    def get_queryset(self):
        entity_id = self.request.session.get('selected_entity_id')
        queryset = CashPaymentLine.objects.filter(entity_id=entity_id).order_by('-date')
        
        # Filter by status if provided
        status = self.request.GET.get('status')
        if status in ['DRAFT', 'POSTED']:
            queryset = queryset.filter(status=status)
        
        # Search by description or reference
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                description__icontains=search
            ) | queryset.filter(
                reference_number__icontains=search
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Cash Payments'
        entity_id = self.request.session.get('selected_entity_id')
        context['status_counts'] = {
            'draft': CashPaymentLine.objects.filter(entity_id=entity_id, status='DRAFT').count(),
            'posted': CashPaymentLine.objects.filter(entity_id=entity_id, status='POSTED').count(),
        }
        return context


class BankReceiptCreateView(LoginRequiredMixin, SessionEntityMixin, CreateView):
    """Create new bank receipt transaction."""
    model = BankReceiptLine
    form_class = BankReceiptLineForm
    template_name = 'accounting/bank_receipt_form.html'
    success_url = reverse_lazy('accounting:bank_receipt_list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if not kwargs.get('data'):
            initial = kwargs.get('initial', {})
            initial['date'] = datetime.now().date()
            kwargs['initial'] = initial
        return kwargs
    
    def form_valid(self, form):
        """Process valid form - save in DRAFT state without GL entries."""
        form.instance.entity = self.request.entity
        
        with transaction.atomic():
            try:
                # Save bank receipt in DRAFT state (no GL entry creation yet)
                receipt = form.save(commit=False)
                receipt.workflow_status = 'DRAFT'
                receipt.status = 'DRAFT'
                receipt.save()
                
                # Create audit log
                AuditLog.objects.create(
                    user=self.request.user,
                    action='create_bank_receipt',
                    model_name='BankReceiptLine',
                    object_id=receipt.id,
                    entity=self.request.entity,
                    description=f"Created bank receipt: {receipt.description}"
                )
                
                messages.success(self.request, 'Bank receipt created successfully! Ready for approval workflow.')
            except Exception as e:
                messages.error(self.request, f'Error creating bank receipt: {str(e)}')
                return redirect('accounting:bank_receipt_list')
        
        return redirect(self.success_url)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Create Bank Receipt'
        context['breadcrumb'] = [
            {'name': 'Dashboard', 'url': '/accounting/dashboard/'},
            {'name': 'Cash Management', 'url': '#'},
            {'name': 'Bank Receipts', 'url': 'bank_receipt_list'},
            {'name': 'New Receipt', 'url': '#'},
        ]
        return context


class BankReceiptListView(LoginRequiredMixin, SessionEntityMixin, ListView):
    """List all bank receipts for current entity."""
    model = BankReceiptLine
    template_name = 'accounting/bank_receipt_list.html'
    context_object_name = 'receipts'
    paginate_by = 50
    
    def get_queryset(self):
        entity_id = self.request.session.get('selected_entity_id')
        queryset = BankReceiptLine.objects.filter(entity_id=entity_id).order_by('-date')
        
        # Filter by status if provided
        status = self.request.GET.get('status')
        if status in ['DRAFT', 'POSTED']:
            queryset = queryset.filter(status=status)
        
        # Search by description or reference
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                description__icontains=search
            ) | queryset.filter(
                reference_number__icontains=search
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Bank Receipts'
        entity_id = self.request.session.get('selected_entity_id')
        context['status_counts'] = {
            'draft': BankReceiptLine.objects.filter(entity_id=entity_id, status='DRAFT').count(),
            'posted': BankReceiptLine.objects.filter(entity_id=entity_id, status='POSTED').count(),
        }
        return context


class BankPaymentCreateView(LoginRequiredMixin, SessionEntityMixin, CreateView):
    """Create new bank payment transaction."""
    model = BankPaymentLine
    form_class = BankPaymentLineForm
    template_name = 'accounting/bank_payment_form.html'
    success_url = reverse_lazy('accounting:bank_payment_list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if not kwargs.get('data'):
            initial = kwargs.get('initial', {})
            initial['date'] = datetime.now().date()
            kwargs['initial'] = initial
        return kwargs
    
    def form_valid(self, form):
        """Process valid form and create GL entries."""
        form.instance.entity = self.request.entity
        
        with transaction.atomic():
            try:
                # Save bank payment in DRAFT state (no GL entry creation yet)
                payment = form.save(commit=False)
                payment.workflow_status = 'DRAFT'
                payment.status = 'DRAFT'
                payment.save()
                
                # Create audit log
                AuditLog.objects.create(
                    user=self.request.user,
                    action='create_bank_payment',
                    model_name='BankPaymentLine',
                    object_id=payment.id,
                    entity=self.request.entity,
                    description=f"Created bank payment: {payment.description}"
                )
                
                messages.success(self.request, 'Bank payment created successfully! Ready for approval workflow.')
            except Exception as e:
                messages.error(self.request, f'Error creating bank payment: {str(e)}')
                return redirect('accounting:bank_payment_list')
        
        return redirect(self.success_url)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Create Bank Payment'
        context['breadcrumb'] = [
            {'name': 'Dashboard', 'url': '/accounting/dashboard/'},
            {'name': 'Cash Management', 'url': '#'},
            {'name': 'Bank Payments', 'url': 'bank_payment_list'},
            {'name': 'New Payment', 'url': '#'},
        ]
        return context


class BankPaymentListView(LoginRequiredMixin, SessionEntityMixin, ListView):
    """List all bank payments for current entity."""
    model = BankPaymentLine
    template_name = 'accounting/bank_payment_list.html'
    context_object_name = 'payments'
    paginate_by = 50
    
    def get_queryset(self):
        entity_id = self.request.session.get('selected_entity_id')
        queryset = BankPaymentLine.objects.filter(entity_id=entity_id).order_by('-date')
        
        # Filter by status if provided
        status = self.request.GET.get('status')
        if status in ['DRAFT', 'POSTED']:
            queryset = queryset.filter(status=status)
        
        # Search by description or reference
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                description__icontains=search
            ) | queryset.filter(
                reference_number__icontains=search
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Bank Payments'
        entity_id = self.request.session.get('selected_entity_id')
        context['status_counts'] = {
            'draft': BankPaymentLine.objects.filter(entity_id=entity_id, status='DRAFT').count(),
            'posted': BankPaymentLine.objects.filter(entity_id=entity_id, status='POSTED').count(),
        }
        return context


# ============ DETAIL AND PRINT VIEWS ============

class CashReceiptDetailView(LoginRequiredMixin, SessionEntityMixin, DetailView):
    """View details of a cash receipt."""
    model = CashReceiptLine
    template_name = 'accounting/cash_receipt_detail.html'
    context_object_name = 'receipt'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'View Cash Receipt'
        return context


class CashReceiptPrintView(LoginRequiredMixin, SessionEntityMixin, DetailView):
    """Print view for cash receipt."""
    model = CashReceiptLine
    template_name = 'accounting/cash_receipt_print.html'
    context_object_name = 'receipt'


class CashPaymentDetailView(LoginRequiredMixin, SessionEntityMixin, DetailView):
    """View details of a cash payment."""
    model = CashPaymentLine
    template_name = 'accounting/cash_payment_detail.html'
    context_object_name = 'payment'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'View Cash Payment'
        return context


class CashPaymentPrintView(LoginRequiredMixin, SessionEntityMixin, DetailView):
    """Print view for cash payment."""
    model = CashPaymentLine
    template_name = 'accounting/cash_payment_print.html'
    context_object_name = 'payment'


class BankReceiptDetailView(LoginRequiredMixin, SessionEntityMixin, DetailView):
    """View details of a bank receipt."""
    model = BankReceiptLine
    template_name = 'accounting/bank_receipt_detail.html'
    context_object_name = 'receipt'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'View Bank Receipt'
        return context


class BankReceiptPrintView(LoginRequiredMixin, SessionEntityMixin, DetailView):
    """Print view for bank receipt."""
    model = BankReceiptLine
    template_name = 'accounting/bank_receipt_print.html'
    context_object_name = 'receipt'


class BankPaymentDetailView(LoginRequiredMixin, SessionEntityMixin, DetailView):
    """View details of a bank payment."""
    model = BankPaymentLine
    template_name = 'accounting/bank_payment_detail.html'
    context_object_name = 'payment'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'View Bank Payment'
        return context


class BankPaymentPrintView(LoginRequiredMixin, SessionEntityMixin, DetailView):
    """Print view for bank payment."""
    model = BankPaymentLine
    template_name = 'accounting/bank_payment_print.html'
    context_object_name = 'payment'
