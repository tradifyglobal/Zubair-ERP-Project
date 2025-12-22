"""
Journal Voucher Views - CRUD operations with validation and posting
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db import transaction
from django.urls import reverse_lazy
from django.http import JsonResponse, HttpResponseRedirect
from decimal import Decimal
from django.utils import timezone
from django.db.models import Q, Sum

from .models import JournalVoucher, JournalVoucherLine, Entity, LedgerEntry
from .forms_journal_voucher import (
    JournalVoucherForm, 
    JournalVoucherLineFormSet,
    JournalVoucherFilterForm
)
from .mixins import SessionEntityMixin


class JournalVoucherListView(LoginRequiredMixin, SessionEntityMixin, ListView):
    """List all journal vouchers"""
    model = JournalVoucher
    template_name = 'accounting/journal_voucher_list.html'
    context_object_name = 'vouchers'
    paginate_by = 25
    
    def get_queryset(self):
        entity = self.request.entity
        if not entity:
            return JournalVoucher.objects.none()
        
        queryset = JournalVoucher.objects.filter(entity=entity).select_related(
            'entity', 'prepared_by', 'approved_by', 'posted_by'
        ).prefetch_related('lines')
        
        # Apply filters
        voucher_type = self.request.GET.get('voucher_type')
        if voucher_type:
            queryset = queryset.filter(voucher_type=voucher_type)
        
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        date_from = self.request.GET.get('date_from')
        if date_from:
            queryset = queryset.filter(voucher_date__gte=date_from)
        
        date_to = self.request.GET.get('date_to')
        if date_to:
            queryset = queryset.filter(voucher_date__lte=date_to)
        
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(voucher_number__icontains=search) |
                Q(description__icontains=search) |
                Q(reference_number__icontains=search)
            )
        
        return queryset.order_by('-voucher_date', '-voucher_number')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = JournalVoucherFilterForm(self.request.GET)
        context['entity'] = self.request.entity
        return context


class JournalVoucherDetailView(LoginRequiredMixin, SessionEntityMixin, DetailView):
    """View journal voucher details"""
    model = JournalVoucher
    template_name = 'accounting/journal_voucher_detail.html'
    context_object_name = 'voucher'
    
    def get_queryset(self):
        entity = self.request.entity
        if not entity:
            return JournalVoucher.objects.none()
        return JournalVoucher.objects.filter(entity=entity)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        voucher = self.get_object()
        
        # Calculate totals
        lines = voucher.lines.all()
        context['total_debit'] = voucher.get_total_debit()
        context['total_credit'] = voucher.get_total_credit()
        context['is_balanced'] = voucher.is_balanced()
        context['lines'] = lines
        
        return context


class JournalVoucherCreateView(LoginRequiredMixin, SessionEntityMixin, CreateView):
    """Create new journal voucher"""
    model = JournalVoucher
    form_class = JournalVoucherForm
    template_name = 'accounting/journal_voucher_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        entity = self.request.entity
        
        if self.request.POST:
            context['formset'] = JournalVoucherLineFormSet(
                self.request.POST,
                instance=self.object,
                form_kwargs={'entity': entity}
            )
        else:
            context['formset'] = JournalVoucherLineFormSet(
                instance=self.object,
                form_kwargs={'entity': entity}
            )
        
        context['entity'] = entity
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        
        # Validate formset
        if not formset.is_valid():
            return self.form_invalid(form)
        
        # Check if voucher is balanced
        total_debit = Decimal('0')
        total_credit = Decimal('0')
        
        for line_form in formset:
            if line_form.cleaned_data and not line_form.cleaned_data.get('DELETE', False):
                amount = line_form.cleaned_data.get('amount', Decimal('0'))
                entry_type = line_form.cleaned_data.get('entry_type')
                
                if entry_type == 'DEBIT':
                    total_debit += amount
                elif entry_type == 'CREDIT':
                    total_credit += amount
        
        if total_debit != total_credit:
            messages.error(
                self.request, 
                f'Voucher is not balanced! Total Debits: ₹{total_debit:,.2f}, Total Credits: ₹{total_credit:,.2f}'
            )
            return self.form_invalid(form)
        
        with transaction.atomic():
            # Set entity and user
            entity = self.request.entity
            form.instance.entity = entity
            form.instance.prepared_by = self.request.user
            form.instance.created_by = self.request.user
            form.instance.status = 'DRAFT'
            
            # Save voucher
            self.object = form.save()
            
            # Save formset
            formset.instance = self.object
            formset.save()
        
        messages.success(
            self.request, 
            f'Journal Voucher {self.object.voucher_number} created successfully!'
        )
        return HttpResponseRedirect(self.get_success_url())
    
    def get_success_url(self):
        return reverse_lazy('accounting:journal_voucher_detail', kwargs={'pk': self.object.pk})


class JournalVoucherUpdateView(LoginRequiredMixin, SessionEntityMixin, UpdateView):
    """Update existing journal voucher (only if DRAFT)"""
    model = JournalVoucher
    form_class = JournalVoucherForm
    template_name = 'accounting/journal_voucher_form.html'
    
    def get_queryset(self):
        entity = self.request.entity
        if not entity:
            return JournalVoucher.objects.none()
        # Only allow editing DRAFT vouchers
        return JournalVoucher.objects.filter(entity=entity, status='DRAFT')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        entity = self.request.entity
        
        if self.request.POST:
            context['formset'] = JournalVoucherLineFormSet(
                self.request.POST,
                instance=self.object,
                form_kwargs={'entity': entity}
            )
        else:
            context['formset'] = JournalVoucherLineFormSet(
                instance=self.object,
                form_kwargs={'entity': entity}
            )
        
        context['entity'] = entity
        context['is_update'] = True
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        
        # Validate formset
        if not formset.is_valid():
            return self.form_invalid(form)
        
        # Check if voucher is balanced
        total_debit = Decimal('0')
        total_credit = Decimal('0')
        
        for line_form in formset:
            if line_form.cleaned_data and not line_form.cleaned_data.get('DELETE', False):
                amount = line_form.cleaned_data.get('amount', Decimal('0'))
                entry_type = line_form.cleaned_data.get('entry_type')
                
                if entry_type == 'DEBIT':
                    total_debit += amount
                elif entry_type == 'CREDIT':
                    total_credit += amount
        
        if total_debit != total_credit:
            messages.error(
                self.request, 
                f'Voucher is not balanced! Total Debits: ₹{total_debit:,.2f}, Total Credits: ₹{total_credit:,.2f}'
            )
            return self.form_invalid(form)
        
        with transaction.atomic():
            # Save voucher
            self.object = form.save()
            
            # Save formset
            formset.instance = self.object
            formset.save()
        
        messages.success(
            self.request, 
            f'Journal Voucher {self.object.voucher_number} updated successfully!'
        )
        return HttpResponseRedirect(self.get_success_url())
    
    def get_success_url(self):
        return reverse_lazy('accounting:journal_voucher_detail', kwargs={'pk': self.object.pk})


class JournalVoucherDeleteView(LoginRequiredMixin, SessionEntityMixin, DeleteView):
    """Delete journal voucher (only if DRAFT)"""
    model = JournalVoucher
    template_name = 'accounting/journal_voucher_confirm_delete.html'
    success_url = reverse_lazy('accounting:journal_voucher_list')
    
    def get_queryset(self):
        entity = self.request.entity
        if not entity:
            return JournalVoucher.objects.none()
        # Only allow deleting DRAFT vouchers
        return JournalVoucher.objects.filter(entity=entity, status='DRAFT')
    
    def delete(self, request, *args, **kwargs):
        voucher = self.get_object()
        voucher_number = voucher.voucher_number
        
        messages.success(request, f'Journal Voucher {voucher_number} deleted successfully!')
        return super().delete(request, *args, **kwargs)


def journal_voucher_post(request, pk):
    """Post journal voucher to ledger"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST request required'}, status=400)
    
    voucher = get_object_or_404(JournalVoucher, pk=pk)
    
    # Check if already posted
    if voucher.is_posted:
        messages.error(request, 'Voucher is already posted!')
        return redirect('accounting:journal_voucher_detail', pk=pk)
    
    # Check if balanced
    if not voucher.is_balanced():
        messages.error(request, 'Cannot post unbalanced voucher!')
        return redirect('accounting:journal_voucher_detail', pk=pk)
    
    # Check if approved (optional - remove if approval not required)
    if voucher.status not in ['APPROVED', 'DRAFT']:
        messages.error(request, 'Voucher must be approved before posting!')
        return redirect('accounting:journal_voucher_detail', pk=pk)
    
    try:
        with transaction.atomic():
            voucher.post(user=request.user)
        
        messages.success(
            request, 
            f'Journal Voucher {voucher.voucher_number} posted successfully!'
        )
    except Exception as e:
        messages.error(request, f'Error posting voucher: {str(e)}')
    
    return redirect('accounting:journal_voucher_detail', pk=pk)


def journal_voucher_approve(request, pk):
    """Approve journal voucher"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST request required'}, status=400)
    
    voucher = get_object_or_404(JournalVoucher, pk=pk)
    
    if voucher.status != 'PENDING_APPROVAL' and voucher.status != 'DRAFT':
        messages.error(request, 'Voucher cannot be approved in current status!')
        return redirect('accounting:journal_voucher_detail', pk=pk)
    
    if not voucher.is_balanced():
        messages.error(request, 'Cannot approve unbalanced voucher!')
        return redirect('accounting:journal_voucher_detail', pk=pk)
    
    voucher.status = 'APPROVED'
    voucher.approved_by = request.user
    voucher.approved_date = timezone.now()
    voucher.save()
    
    messages.success(
        request, 
        f'Journal Voucher {voucher.voucher_number} approved successfully!'
    )
    return redirect('accounting:journal_voucher_detail', pk=pk)


def journal_voucher_submit(request, pk):
    """Submit voucher for approval"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST request required'}, status=400)
    
    voucher = get_object_or_404(JournalVoucher, pk=pk)
    
    if voucher.status != 'DRAFT':
        messages.error(request, 'Only draft vouchers can be submitted!')
        return redirect('accounting:journal_voucher_detail', pk=pk)
    
    if not voucher.is_balanced():
        messages.error(request, 'Cannot submit unbalanced voucher!')
        return redirect('accounting:journal_voucher_detail', pk=pk)
    
    voucher.status = 'PENDING_APPROVAL'
    voucher.save()
    
    messages.success(
        request, 
        f'Journal Voucher {voucher.voucher_number} submitted for approval!'
    )
    return redirect('accounting:journal_voucher_detail', pk=pk)
