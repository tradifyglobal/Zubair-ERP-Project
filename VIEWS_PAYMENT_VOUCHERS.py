"""
PAYMENT VIEWS - Cash & Bank Payment Workflows
Views for managing payment vouchers, approvals, and reporting
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, FormView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from django.db.models import Q, Sum, Count, F
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.db import transaction
from decimal import Decimal
import json

from accounting.models import (
    CashPaymentVoucher, CashPaymentLine,
    BankPaymentVoucher, BankPaymentLine,
    GLAccount, JournalEntry, Entity
)
from accounting.forms import CashPaymentVoucherForm, BankPaymentVoucherForm
from accounting.mixins import SessionEntityMixin


# ============================================================================
# CASH PAYMENT VOUCHER VIEWS
# ============================================================================

class CashPaymentListView(LoginRequiredMixin, SessionEntityMixin, ListView):
    """
    List all cash payment vouchers with filtering options
    """
    model = CashPaymentVoucher
    template_name = 'accounting/cash_payment_list.html'
    context_object_name = 'vouchers'
    paginate_by = 50
    
    def get_queryset(self):
        queryset = CashPaymentVoucher.objects.filter(
            entity=self.entity
        ).select_related(
            'maker', 'checker', 'approver', 'journal_entry'
        ).prefetch_related('lines')
        
        # Filters
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        payee = self.request.GET.get('payee')
        if payee:
            queryset = queryset.filter(payee_name__icontains=payee)
        
        date_from = self.request.GET.get('date_from')
        if date_from:
            queryset = queryset.filter(voucher_date__gte=date_from)
        
        date_to = self.request.GET.get('date_to')
        if date_to:
            queryset = queryset.filter(voucher_date__lte=date_to)
        
        return queryset.order_by('-voucher_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Summary statistics
        total = CashPaymentVoucher.objects.filter(
            entity=self.entity
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
        
        pending = CashPaymentVoucher.objects.filter(
            entity=self.entity,
            status__in=['DRAFT', 'SUBMITTED_FOR_APPROVAL', 'CHECKED']
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
        
        posted = CashPaymentVoucher.objects.filter(
            entity=self.entity,
            status='GL_POSTED'
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
        
        context.update({
            'total_amount': total,
            'pending_amount': pending,
            'posted_amount': posted,
            'status_choices': CashPaymentVoucher.STATUS_CHOICES,
            'current_filters': {
                'status': self.request.GET.get('status', ''),
                'payee': self.request.GET.get('payee', ''),
                'date_from': self.request.GET.get('date_from', ''),
                'date_to': self.request.GET.get('date_to', ''),
            }
        })
        
        return context


class CashPaymentDetailView(LoginRequiredMixin, SessionEntityMixin, DetailView):
    """
    View details of a cash payment voucher with GL entries
    """
    model = CashPaymentVoucher
    template_name = 'accounting/cash_payment_detail.html'
    context_object_name = 'voucher'
    
    def get_queryset(self):
        return CashPaymentVoucher.objects.filter(
            entity=self.entity
        ).select_related(
            'maker', 'checker', 'approver', 'journal_entry'
        ).prefetch_related('lines')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        voucher = self.get_object()
        
        # Get GL entries if posted
        gl_entries = []
        if voucher.journal_entry:
            gl_entries = voucher.journal_entry.entries.all()
        
        context['gl_entries'] = gl_entries
        context['can_submit'] = voucher.can_submit() and self.request.user == voucher.maker
        context['can_approve'] = voucher.can_approve() and self.request.user.has_perm('accounting.can_approve_cash_payment')
        context['can_authorize'] = voucher.can_authorize() and self.request.user.has_perm('accounting.can_authorize_cash_payment')
        context['can_reverse'] = voucher.can_reverse() and self.request.user.has_perm('accounting.can_reverse_cash_payment')
        
        return context


class CashPaymentCreateView(LoginRequiredMixin, SessionEntityMixin, CreateView):
    """
    Create a new cash payment voucher
    """
    model = CashPaymentVoucher
    form_class = CashPaymentVoucherForm
    template_name = 'accounting/cash_payment_form.html'
    success_url = reverse_lazy('accounting:cash_payment_list')
    
    def form_valid(self, form):
        """Set entity and maker before saving"""
        form.instance.entity = self.entity
        form.instance.maker = self.request.user
        form.instance.created_by = self.request.user
        
        # Generate voucher number
        last_voucher = CashPaymentVoucher.objects.filter(
            entity=self.entity,
            voucher_number__startswith='CPV/'
        ).order_by('-id').first()
        
        if last_voucher:
            # Extract number and increment
            parts = last_voucher.voucher_number.split('/')
            number = int(parts[-1]) + 1
        else:
            number = 1
        
        year = form.instance.voucher_date.year
        form.instance.voucher_number = f'CPV/{year}/{number:04d}'
        
        response = super().form_valid(form)
        
        # Handle line items from AJAX
        lines_data = self.request.POST.getlist('line_data')
        for line_json in lines_data:
            if line_json:
                line_data = json.loads(line_json)
                CashPaymentLine.objects.create(
                    voucher=self.object,
                    line_number=line_data['line_number'],
                    description=line_data['description'],
                    amount=Decimal(line_data['amount']),
                    expense_account_id=line_data['expense_account_id'],
                    tax_amount=Decimal(line_data.get('tax_amount', 0)),
                    tax_rate=Decimal(line_data.get('tax_rate', 0)),
                    document_reference=line_data.get('document_reference', '')
                )
        
        messages.success(self.request, 'Cash Payment Voucher created successfully')
        return response


class CashPaymentApprovalView(LoginRequiredMixin, PermissionRequiredMixin, SessionEntityMixin, FormView):
    """
    Approve a cash payment voucher (Checker role)
    """
    template_name = 'accounting/cash_payment_approval.html'
    permission_required = 'accounting.can_approve_cash_payment'
    success_url = reverse_lazy('accounting:cash_payment_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        voucher = get_object_or_404(
            CashPaymentVoucher,
            pk=self.kwargs['pk'],
            entity=self.entity
        )
        context['voucher'] = voucher
        context['can_approve'] = voucher.can_approve()
        return context
    
    def post(self, request, *args, **kwargs):
        voucher = get_object_or_404(
            CashPaymentVoucher,
            pk=self.kwargs['pk'],
            entity=self.entity
        )
        
        action = request.POST.get('action')
        comments = request.POST.get('comments', '')
        
        if action == 'approve' and voucher.can_approve():
            voucher.status = 'CHECKED'
            voucher.checker = request.user
            voucher.checker_date = timezone.now()
            voucher.checker_comments = comments
            voucher.save()
            messages.success(request, 'Cash Payment Voucher approved')
        
        elif action == 'reject' and voucher.can_approve():
            voucher.status = 'REJECTED'
            voucher.checker = request.user
            voucher.checker_date = timezone.now()
            voucher.checker_comments = comments
            voucher.save()
            messages.warning(request, 'Cash Payment Voucher rejected')
        
        return redirect('accounting:cash_payment_detail', pk=voucher.pk)


class CashPaymentAuthorizationView(LoginRequiredMixin, PermissionRequiredMixin, SessionEntityMixin, FormView):
    """
    Authorize a cash payment voucher (Approver role)
    Triggers GL posting automatically via signal
    """
    template_name = 'accounting/cash_payment_authorization.html'
    permission_required = 'accounting.can_authorize_cash_payment'
    success_url = reverse_lazy('accounting:cash_payment_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        voucher = get_object_or_404(
            CashPaymentVoucher,
            pk=self.kwargs['pk'],
            entity=self.entity
        )
        context['voucher'] = voucher
        context['can_authorize'] = voucher.can_authorize()
        
        # Preview GL entries
        gl_preview = []
        for line in voucher.lines.all():
            gl_preview.append({
                'account': line.expense_account.name,
                'code': line.expense_account.code,
                'debit': line.amount,
                'credit': Decimal('0.00')
            })
        
        # Add cash account credit
        gl_preview.append({
            'account': 'Cash Account',
            'code': '100-CASH',
            'debit': Decimal('0.00'),
            'credit': voucher.total_amount
        })
        
        context['gl_preview'] = gl_preview
        return context
    
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        voucher = get_object_or_404(
            CashPaymentVoucher,
            pk=self.kwargs['pk'],
            entity=self.entity
        )
        
        action = request.POST.get('action')
        comments = request.POST.get('comments', '')
        
        if action == 'authorize' and voucher.can_authorize():
            voucher.status = 'AUTHORIZED'
            voucher.approver = request.user
            voucher.approver_date = timezone.now()
            voucher.approver_comments = comments
            voucher.save()
            
            # Signal handler will create GL entries
            messages.success(request, 'Cash Payment Voucher authorized and GL entries posted')
        
        elif action == 'reject' and voucher.can_authorize():
            voucher.status = 'REJECTED'
            voucher.approver = request.user
            voucher.approver_date = timezone.now()
            voucher.approver_comments = comments
            voucher.save()
            messages.warning(request, 'Cash Payment Voucher rejected')
        
        return redirect('accounting:cash_payment_detail', pk=voucher.pk)


# ============================================================================
# BANK PAYMENT VOUCHER VIEWS
# ============================================================================

class BankPaymentListView(LoginRequiredMixin, SessionEntityMixin, ListView):
    """
    List all bank payment vouchers with filtering options
    """
    model = BankPaymentVoucher
    template_name = 'accounting/bank_payment_list.html'
    context_object_name = 'vouchers'
    paginate_by = 50
    
    def get_queryset(self):
        queryset = BankPaymentVoucher.objects.filter(
            entity=self.entity
        ).select_related(
            'maker', 'checker', 'approver', 'journal_entry', 'bank_account'
        ).prefetch_related('lines')
        
        # Filters
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        payee = self.request.GET.get('payee')
        if payee:
            queryset = queryset.filter(payee_name__icontains=payee)
        
        date_from = self.request.GET.get('date_from')
        if date_from:
            queryset = queryset.filter(voucher_date__gte=date_from)
        
        date_to = self.request.GET.get('date_to')
        if date_to:
            queryset = queryset.filter(voucher_date__lte=date_to)
        
        return queryset.order_by('-voucher_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Summary statistics
        total = BankPaymentVoucher.objects.filter(
            entity=self.entity
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
        
        pending = BankPaymentVoucher.objects.filter(
            entity=self.entity,
            status__in=['DRAFT', 'SUBMITTED_FOR_APPROVAL', 'CHECKED']
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
        
        posted = BankPaymentVoucher.objects.filter(
            entity=self.entity,
            status__in=['GL_POSTED', 'IN_TRANSIT', 'CLEARED']
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
        
        context.update({
            'total_amount': total,
            'pending_amount': pending,
            'posted_amount': posted,
            'status_choices': BankPaymentVoucher.STATUS_CHOICES,
            'current_filters': {
                'status': self.request.GET.get('status', ''),
                'payee': self.request.GET.get('payee', ''),
                'date_from': self.request.GET.get('date_from', ''),
                'date_to': self.request.GET.get('date_to', ''),
            }
        })
        
        return context


class BankPaymentDetailView(LoginRequiredMixin, SessionEntityMixin, DetailView):
    """
    View details of a bank payment voucher with GL entries
    """
    model = BankPaymentVoucher
    template_name = 'accounting/bank_payment_detail.html'
    context_object_name = 'voucher'
    
    def get_queryset(self):
        return BankPaymentVoucher.objects.filter(
            entity=self.entity
        ).select_related(
            'maker', 'checker', 'approver', 'journal_entry', 'bank_account'
        ).prefetch_related('lines')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        voucher = self.get_object()
        
        # Get GL entries if posted
        gl_entries = []
        if voucher.journal_entry:
            gl_entries = voucher.journal_entry.entries.all()
        
        context['gl_entries'] = gl_entries
        context['can_submit'] = voucher.can_submit() and self.request.user == voucher.maker
        context['can_approve'] = voucher.can_approve() and self.request.user.has_perm('accounting.can_approve_bank_payment')
        context['can_authorize'] = voucher.can_authorize() and self.request.user.has_perm('accounting.can_authorize_bank_payment')
        context['can_reverse'] = voucher.can_reverse() and self.request.user.has_perm('accounting.can_reverse_bank_payment')
        
        return context


class BankPaymentCreateView(LoginRequiredMixin, SessionEntityMixin, CreateView):
    """
    Create a new bank payment voucher
    """
    model = BankPaymentVoucher
    form_class = BankPaymentVoucherForm
    template_name = 'accounting/bank_payment_form.html'
    success_url = reverse_lazy('accounting:bank_payment_list')
    
    def form_valid(self, form):
        """Set entity and maker before saving"""
        form.instance.entity = self.entity
        form.instance.maker = self.request.user
        form.instance.created_by = self.request.user
        
        # Generate voucher number
        last_voucher = BankPaymentVoucher.objects.filter(
            entity=self.entity,
            voucher_number__startswith='BPV/'
        ).order_by('-id').first()
        
        if last_voucher:
            parts = last_voucher.voucher_number.split('/')
            number = int(parts[-1]) + 1
        else:
            number = 1
        
        year = form.instance.voucher_date.year
        form.instance.voucher_number = f'BPV/{year}/{number:04d}'
        
        response = super().form_valid(form)
        
        # Handle line items from AJAX
        lines_data = self.request.POST.getlist('line_data')
        for line_json in lines_data:
            if line_json:
                line_data = json.loads(line_json)
                BankPaymentLine.objects.create(
                    voucher=self.object,
                    line_number=line_data['line_number'],
                    description=line_data['description'],
                    amount=Decimal(line_data['amount']),
                    net_amount=Decimal(line_data.get('net_amount', line_data['amount'])),
                    payable_account_id=line_data.get('payable_account_id'),
                    expense_account_id=line_data.get('expense_account_id'),
                    tax_amount=Decimal(line_data.get('tax_amount', 0)),
                    tax_rate=Decimal(line_data.get('tax_rate', 0)),
                    po_reference=line_data.get('po_reference', ''),
                    invoice_reference=line_data.get('invoice_reference', '')
                )
        
        messages.success(self.request, 'Bank Payment Voucher created successfully')
        return response


class BankPaymentApprovalView(LoginRequiredMixin, PermissionRequiredMixin, SessionEntityMixin, FormView):
    """
    Approve a bank payment voucher (Checker role)
    """
    template_name = 'accounting/bank_payment_approval.html'
    permission_required = 'accounting.can_approve_bank_payment'
    success_url = reverse_lazy('accounting:bank_payment_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        voucher = get_object_or_404(
            BankPaymentVoucher,
            pk=self.kwargs['pk'],
            entity=self.entity
        )
        context['voucher'] = voucher
        context['can_approve'] = voucher.can_approve()
        return context
    
    def post(self, request, *args, **kwargs):
        voucher = get_object_or_404(
            BankPaymentVoucher,
            pk=self.kwargs['pk'],
            entity=self.entity
        )
        
        action = request.POST.get('action')
        comments = request.POST.get('comments', '')
        
        if action == 'approve' and voucher.can_approve():
            voucher.status = 'CHECKED'
            voucher.checker = request.user
            voucher.checker_date = timezone.now()
            voucher.checker_comments = comments
            voucher.save()
            messages.success(request, 'Bank Payment Voucher approved')
        
        elif action == 'reject' and voucher.can_approve():
            voucher.status = 'REJECTED'
            voucher.checker = request.user
            voucher.checker_date = timezone.now()
            voucher.checker_comments = comments
            voucher.save()
            messages.warning(request, 'Bank Payment Voucher rejected')
        
        return redirect('accounting:bank_payment_detail', pk=voucher.pk)


class BankPaymentAuthorizationView(LoginRequiredMixin, PermissionRequiredMixin, SessionEntityMixin, FormView):
    """
    Authorize a bank payment voucher (Approver role)
    Triggers GL posting and bank transfer initiation
    """
    template_name = 'accounting/bank_payment_authorization.html'
    permission_required = 'accounting.can_authorize_bank_payment'
    success_url = reverse_lazy('accounting:bank_payment_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        voucher = get_object_or_404(
            BankPaymentVoucher,
            pk=self.kwargs['pk'],
            entity=self.entity
        )
        context['voucher'] = voucher
        context['can_authorize'] = voucher.can_authorize()
        
        # Preview GL entries
        gl_preview = []
        for line in voucher.lines.all():
            account = line.payable_account or line.expense_account
            gl_preview.append({
                'account': account.name,
                'code': account.code,
                'debit': line.amount,
                'credit': Decimal('0.00')
            })
        
        # Add bank account credit
        gl_preview.append({
            'account': voucher.bank_account.account_name,
            'code': voucher.bank_account.account_code,
            'debit': Decimal('0.00'),
            'credit': voucher.total_amount
        })
        
        context['gl_preview'] = gl_preview
        return context
    
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        voucher = get_object_or_404(
            BankPaymentVoucher,
            pk=self.kwargs['pk'],
            entity=self.entity
        )
        
        action = request.POST.get('action')
        comments = request.POST.get('comments', '')
        
        if action == 'authorize' and voucher.can_authorize():
            voucher.status = 'AUTHORIZED'
            voucher.approver = request.user
            voucher.approver_date = timezone.now()
            voucher.approver_comments = comments
            voucher.save()
            
            # Signal handler will create GL entries and initiate bank transfer
            messages.success(request, 'Bank Payment Voucher authorized, GL entries posted, and bank transfer initiated')
        
        elif action == 'reject' and voucher.can_authorize():
            voucher.status = 'REJECTED'
            voucher.approver = request.user
            voucher.approver_date = timezone.now()
            voucher.approver_comments = comments
            voucher.save()
            messages.warning(request, 'Bank Payment Voucher rejected')
        
        return redirect('accounting:bank_payment_detail', pk=voucher.pk)


# ============================================================================
# PAYMENT REPORTING VIEWS
# ============================================================================

class PaymentDashboardView(LoginRequiredMixin, SessionEntityMixin, TemplateView):
    """
    Dashboard showing payment summary and trends
    """
    template_name = 'accounting/payment_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Cash payment summary
        cash_total = CashPaymentVoucher.objects.filter(
            entity=self.entity, status='GL_POSTED'
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
        
        cash_pending = CashPaymentVoucher.objects.filter(
            entity=self.entity,
            status__in=['DRAFT', 'SUBMITTED_FOR_APPROVAL', 'CHECKED', 'AUTHORIZED']
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
        
        # Bank payment summary
        bank_total = BankPaymentVoucher.objects.filter(
            entity=self.entity,
            status__in=['GL_POSTED', 'IN_TRANSIT', 'CLEARED']
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
        
        bank_pending = BankPaymentVoucher.objects.filter(
            entity=self.entity,
            status__in=['DRAFT', 'SUBMITTED_FOR_APPROVAL', 'CHECKED', 'AUTHORIZED']
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
        
        # Recent vouchers
        recent_cash = CashPaymentVoucher.objects.filter(
            entity=self.entity
        ).order_by('-voucher_date')[:10]
        
        recent_bank = BankPaymentVoucher.objects.filter(
            entity=self.entity
        ).order_by('-voucher_date')[:10]
        
        # Pending approvals
        pending_approval = CashPaymentVoucher.objects.filter(
            entity=self.entity,
            status='SUBMITTED_FOR_APPROVAL'
        ).count() + BankPaymentVoucher.objects.filter(
            entity=self.entity,
            status='SUBMITTED_FOR_APPROVAL'
        ).count()
        
        context.update({
            'cash_total': cash_total,
            'cash_pending': cash_pending,
            'bank_total': bank_total,
            'bank_pending': bank_pending,
            'recent_cash': recent_cash,
            'recent_bank': recent_bank,
            'pending_approval': pending_approval,
        })
        
        return context


from django.utils import timezone
