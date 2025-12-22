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
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
from decimal import Decimal
from .models import (
    CashReceiptLine, CashPaymentLine, BankReceiptLine, BankPaymentLine,
    Account, LedgerEntry, AuditLog, Entity
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
        # Get entity from session
        entity_id = self.request.session.get('selected_entity_id')
        if entity_id:
            entity = Entity.objects.filter(id=entity_id, is_active=True).first()
            kwargs['entity'] = entity
        return kwargs
    
    def form_valid(self, form):
        """Process valid form and save as DRAFT without creating GL entries yet."""
        form.instance.entity = self.request.entity
        form.instance.workflow_status = 'DRAFT'
        form.instance.status = 'DRAFT'
        
        # Auto-assign stakeholder based on selected account BEFORE saving
        if not form.instance.stakeholder_id and form.instance.account:
            stakeholder = self._find_stakeholder_for_account(form.instance.account)
            if stakeholder:
                form.instance.stakeholder = stakeholder
        
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
    
    def _find_stakeholder_for_account(self, account):
        """Find stakeholder that matches the account name pattern."""
        from accounting.models import Stakeholder
        
        if not account or not account.name:
            return None
            
        account_name = account.name.strip()
        
        # Extract stakeholder name from account name patterns like:
        # "Dr. Irfan Mohammed - Capital" -> "Dr. Irfan Mohammed"
        # "Nasir Ali Ali Mohammed - Capital" -> "Nasir Ali Ali Mohammed"
        if ' - Capital' in account_name:
            stakeholder_name = account_name.replace(' - Capital', '').strip()
        else:
            return None
        
        # Try to find matching stakeholder by name
        stakeholders = Stakeholder.objects.filter(entity=account.entity)
        
        # 1. First, try exact match by full name
        for stakeholder in stakeholders:
            if stakeholder.full_name == stakeholder_name:
                return stakeholder
        
        # 2. Try fuzzy matching for name variations
        extracted_words = set(stakeholder_name.lower().split())
        best_match = None
        best_score = 0
        
        for stakeholder in stakeholders:
            stakeholder_words = set(stakeholder.full_name.lower().split())
            
            # Calculate word overlap
            overlap = len(extracted_words.intersection(stakeholder_words))
            total_words = max(len(extracted_words), len(stakeholder_words))
            
            if total_words > 0:
                score = overlap / total_words
                
                # Require at least 60% word match and minimum 2 matching words
                if score >= 0.6 and overlap >= 2 and score > best_score:
                    best_match = stakeholder
                    best_score = score
        
        if best_match:
            return best_match
        
        # 3. Fallback: try partial matching by first/last name
        name_parts = stakeholder_name.split()
        if len(name_parts) >= 2:
            first_part = name_parts[0]
            last_part = name_parts[-1]
            
            for stakeholder in stakeholders:
                if (stakeholder.first_name and stakeholder.last_name and 
                    first_part.lower() in stakeholder.first_name.lower() and 
                    last_part.lower() in stakeholder.last_name.lower()):
                    return stakeholder
        
        return None
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Create Cash Receipt'
        context['breadcrumb'] = [
            {'name': 'Dashboard', 'url': '/accounting/dashboard/'},
            {'name': 'Cash Management', 'url': '#'},
            {'name': 'Cash Receipts', 'url': 'cash_receipt_list'},
            {'name': 'New Receipt', 'url': '#'},
        ]
        # Add entity_id for reference number generation
        entity_id = self.request.session.get('selected_entity_id')
        if entity_id:
            context['entity_id'] = entity_id
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
        # Get entity from session
        entity_id = self.request.session.get('selected_entity_id')
        if entity_id:
            entity = Entity.objects.filter(id=entity_id, is_active=True).first()
            kwargs['entity'] = entity
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
        # Add entity_id for reference number generation
        entity_id = self.request.session.get('selected_entity_id')
        if entity_id:
            context['entity_id'] = entity_id
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
        # Get entity from session
        entity_id = self.request.session.get('selected_entity_id')
        if entity_id:
            entity = Entity.objects.filter(id=entity_id, is_active=True).first()
            kwargs['entity'] = entity
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
        # Add entity_id for reference number generation
        entity_id = self.request.session.get('selected_entity_id')
        if entity_id:
            context['entity_id'] = entity_id
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
        # Get entity from session
        entity_id = self.request.session.get('selected_entity_id')
        if entity_id:
            entity = Entity.objects.filter(id=entity_id, is_active=True).first()
            kwargs['entity'] = entity
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
        # Add entity_id for reference number generation
        entity_id = self.request.session.get('selected_entity_id')
        if entity_id:
            context['entity_id'] = entity_id
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


@require_http_methods(["GET"])
@csrf_exempt
def get_sub_accounts_api(request):
    """
    API endpoint to get sub-accounts for a given main account.
    Used by JavaScript to populate cascading dropdown.
    
    Query params:
        - main_account_id: ID of the main account
        - entity_id: ID of the entity
    
    Returns JSON: {
        'success': bool,
        'sub_accounts': [
            {'id': 1, 'account_number': '3100-01', 'name': 'Account Name'},
            ...
        ]
    }
    """
    try:
        main_account_id = request.GET.get('main_account_id')
        entity_id = request.GET.get('entity_id')
        
        if not main_account_id or not entity_id:
            return JsonResponse({
                'success': False,
                'message': 'main_account_id and entity_id are required'
            }, status=400)
        
        # Get the main account
        main_account = Account.objects.filter(
            id=main_account_id,
            entity_id=entity_id,
            is_active=True
        ).first()
        
        if not main_account:
            return JsonResponse({
                'success': False,
                'message': 'Main account not found'
            }, status=404)
        
        # Get all sub-accounts of this main account
        sub_accounts = Account.objects.filter(
            parent_account=main_account,
            entity_id=entity_id,
            is_active=True
        ).order_by('account_number').values('id', 'account_number', 'name')
        
        # If no sub-accounts exist, include the main account itself as an option
        accounts_list = list(sub_accounts)
        if not accounts_list:
            accounts_list = [{
                'id': main_account.id,
                'account_number': main_account.account_number,
                'name': main_account.name
            }]
        
        return JsonResponse({
            'success': True,
            'sub_accounts': accounts_list,
            'has_sub_accounts': len(sub_accounts) > 0,
            'main_account_fallback': not bool(sub_accounts)
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)


@require_http_methods(["GET"])
def generate_reference_number_api(request):
    """
    API endpoint to generate reference numbers based on form type.
    Used by JavaScript to auto-populate reference number fields.
    
    Query params:
        - form_type: Type of form ('cash_receipt', 'cash_payment', 'bank_receipt', 'bank_payment')
        - entity_id: ID of the entity
    
    Returns JSON: {
        'success': bool,
        'reference_number': 'CR001' or 'CP001' or 'BR001' or 'BP001'
    }
    """
    try:
        form_type = request.GET.get('form_type')
        entity_id = request.GET.get('entity_id')
        
        if not form_type or not entity_id:
            return JsonResponse({
                'success': False,
                'message': 'form_type and entity_id are required'
            }, status=400)
        
        # Determine the prefix and model based on form type
        prefix_map = {
            'cash_receipt': 'CR',
            'cash_payment': 'CP',
            'bank_receipt': 'BR',
            'bank_payment': 'BP'
        }
        
        model_map = {
            'cash_receipt': CashReceiptLine,
            'cash_payment': CashPaymentLine,
            'bank_receipt': BankReceiptLine,
            'bank_payment': BankPaymentLine
        }
        
        if form_type not in prefix_map:
            return JsonResponse({
                'success': False,
                'message': f'Invalid form_type: {form_type}'
            }, status=400)
        
        prefix = prefix_map[form_type]
        model = model_map[form_type]
        
        # Get the highest sequence number for this form type and entity
        latest = model.objects.filter(
            entity_id=entity_id,
            reference_number__startswith=prefix
        ).order_by('-reference_number').first()
        
        if latest and latest.reference_number:
            try:
                # Extract the number from the reference (e.g., 'CR001' -> 1)
                number_part = latest.reference_number[len(prefix):]
                sequence = int(number_part) + 1
            except (ValueError, IndexError):
                sequence = 1
        else:
            sequence = 1
        
        # Generate the reference number with zero-padding (e.g., CR001)
        reference_number = f"{prefix}{sequence:03d}"
        
        return JsonResponse({
            'success': True,
            'reference_number': reference_number
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)
