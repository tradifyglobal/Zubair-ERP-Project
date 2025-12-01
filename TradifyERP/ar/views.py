from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, TemplateView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, Q, Count
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from django.urls import reverse_lazy
from django.contrib import messages

from .models import CustomerInvoice, CustomerPayment, ARAging, ARReconciliation
from .forms import CustomerInvoiceForm, CustomerPaymentForm
from accounting.models import Entity, AuditLog
from accounting.mixins import SessionEntityMixin


class ARDashboardView(SessionEntityMixin, LoginRequiredMixin, TemplateView):
    """AR Dashboard with KPIs."""
    template_name = 'ar/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get session entity
        entity_id = self.request.session.get('selected_entity_id')
        entity = Entity.objects.filter(id=entity_id, is_active=True).first()
        
        today = timezone.now().date()
        
        # Invoice metrics - filtered by entity
        total_invoices = CustomerInvoice.objects.filter(
            entity=entity,
            status__in=['ISSUED', 'SENT', 'PARTIALLY_PAID', 'PAID']
        ).count()
        
        total_outstanding = CustomerInvoice.objects.filter(
            entity=entity,
            status__in=['ISSUED', 'SENT', 'PARTIALLY_PAID']
        ).aggregate(total=Sum('total_amount') - Sum('amount_paid'))['total'] or Decimal('0')
        
        overdue_invoices = CustomerInvoice.objects.filter(
            entity=entity,
            status__in=['ISSUED', 'SENT', 'PARTIALLY_PAID'],
            due_date__lt=today
        )
        overdue_count = overdue_invoices.count()
        overdue_amount = overdue_invoices.aggregate(
            total=Sum('total_amount') - Sum('amount_paid')
        )['total'] or Decimal('0')
        
        # Recent invoices - filtered by entity
        recent_invoices = CustomerInvoice.objects.filter(
            entity=entity,
            status__in=['ISSUED', 'SENT', 'PARTIALLY_PAID', 'PAID']
        ).order_by('-invoice_date')[:10]
        
        # Recent payments - filtered by entity
        recent_payments = CustomerPayment.objects.filter(entity=entity).order_by('-payment_date')[:10]
        
        # DSO (Days Sales Outstanding) - filtered by entity
        paid_invoices = CustomerInvoice.objects.filter(entity=entity, status='PAID', invoice_date__gte=today - timedelta(days=90))
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


class CustomerInvoiceListView(SessionEntityMixin, LoginRequiredMixin, ListView):
    """List all customer invoices."""
    model = CustomerInvoice
    template_name = 'ar/customerinvoice_list.html'
    context_object_name = 'invoices'
    paginate_by = 50
    
    def get_queryset(self):
        queryset = super().get_queryset().select_related('customer', 'entity').order_by('-invoice_date')
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        return queryset


class CustomerInvoiceCreateView(SessionEntityMixin, LoginRequiredMixin, CreateView):
    """Create a new customer invoice."""
    model = CustomerInvoice
    form_class = CustomerInvoiceForm
    template_name = 'ar/customerinvoice_form.html'
    success_url = reverse_lazy('ar:invoice_list')
    
    def post(self, request, *args, **kwargs):
        """Handle form submission."""
        print("\n" + "="*80)
        print("POST DATA RECEIVED:")
        print("="*80)
        for key, value in request.POST.items():
            print(f"  {key}: {value}")
        print("="*80 + "\n")
        return super().post(request, *args, **kwargs)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Get session entity instead of first active entity
        entity_id = self.request.session.get('selected_entity_id')
        entity = Entity.objects.filter(id=entity_id, is_active=True).first()
        if entity:
            kwargs['initial'] = {'entity': entity}
        return kwargs
    
    def form_valid(self, form):
        # Use session entity
        entity_id = self.request.session.get('selected_entity_id')
        entity = Entity.objects.filter(id=entity_id, is_active=True).first()
        
        invoice = form.save(commit=False)
        invoice.entity = entity
        invoice.created_by = self.request.user
        invoice.status = 'DRAFT'
        
        try:
            invoice.save()
            print(f"✓ SUCCESS: Invoice saved!")
            print(f"  ID: {invoice.id}")
            print(f"  Invoice Number: {invoice.invoice_number}")
            print(f"  Total: {invoice.total_amount}")
            
            AuditLog.objects.create(
                entity=entity,
                user=self.request.user.username,
                action='CREATE',
                model_name='CustomerInvoice',
                object_id=invoice.id,
                description=f'Created customer invoice: {invoice.invoice_number}'
            )
            
            messages.success(self.request, f'Customer invoice {invoice.invoice_number} created successfully.')
            print(f"✓ Message added to queue")
            response = super().form_valid(form)
            print(f"✓ Redirecting to: {self.success_url}")
            return response
        except Exception as e:
            print(f"✗ ERROR saving invoice: {str(e)}")
            import traceback
            traceback.print_exc()
            messages.error(self.request, f'Error creating invoice: {str(e)}')
            return self.form_invalid(form)
    
    def form_invalid(self, form):
        """Handle form validation errors with detailed feedback."""
        # Log form errors for debugging
        print("\n" + "="*80)
        print("FORM VALIDATION FAILED")
        print("="*80)
        print(f"Form errors: {form.errors}")
        print(f"Form non-field errors: {form.non_field_errors()}")
        print("="*80 + "\n")
        
        # Add error messages to display in template
        error_count = 0
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"❌ {field.upper()}: {error}")
                error_count += 1
                print(f"  ❌ {field}: {error}")
        
        if form.non_field_errors():
            for error in form.non_field_errors():
                messages.error(self.request, f"❌ Form Error: {error}")
                error_count += 1
                print(f"  ❌ General: {error}")
        
        print(f"Total errors: {error_count}\n")
        return super().form_invalid(form)


class CustomerInvoiceDetailView(SessionEntityMixin, LoginRequiredMixin, DetailView):
    """Detail view for customer invoice."""
    model = CustomerInvoice
    template_name = 'ar/customerinvoice_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['line_items'] = self.object.line_items.all()
        context['payments'] = self.object.reconciliations.all()
        return context


class CustomerInvoiceUpdateView(SessionEntityMixin, LoginRequiredMixin, UpdateView):
    """Update a customer invoice."""
    model = CustomerInvoice
    form_class = CustomerInvoiceForm
    template_name = 'ar/customerinvoice_form.html'
    success_url = reverse_lazy('ar:invoice_list')
    
    def form_valid(self, form):
        invoice = form.save(commit=False)
        
        try:
            invoice.save()
            print(f"✓ SUCCESS: Invoice updated!")
            print(f"  ID: {invoice.id}")
            print(f"  Invoice Number: {invoice.invoice_number}")
            
            AuditLog.objects.create(
                entity=invoice.entity,
                user=self.request.user.username,
                action='UPDATE',
                model_name='CustomerInvoice',
                object_id=invoice.id,
                description=f'Updated customer invoice: {invoice.invoice_number}'
            )
            
            messages.success(self.request, f'Customer invoice {invoice.invoice_number} updated successfully.')
            return super().form_valid(form)
        except Exception as e:
            print(f"✗ ERROR updating invoice: {str(e)}")
            import traceback
            traceback.print_exc()
            messages.error(self.request, f'Error updating invoice: {str(e)}')
            return self.form_invalid(form)
    
    def form_invalid(self, form):
        """Handle form validation errors with detailed feedback."""
        print("\n" + "="*80)
        print("FORM VALIDATION FAILED")
        print("="*80)
        print(f"Form errors: {form.errors}")
        print(f"Form non-field errors: {form.non_field_errors()}")
        print("="*80 + "\n")
        
        error_count = 0
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"❌ {field.upper()}: {error}")
                error_count += 1
                print(f"  ❌ {field}: {error}")
        
        if form.non_field_errors():
            for error in form.non_field_errors():
                messages.error(self.request, f"❌ Form Error: {error}")
                error_count += 1
                print(f"  ❌ General: {error}")
        
        print(f"Total errors: {error_count}\n")
        return super().form_invalid(form)


class CustomerPaymentListView(SessionEntityMixin, LoginRequiredMixin, ListView):
    """List all customer payments."""
    model = CustomerPayment
    template_name = 'ar/customerpayment_list.html'
    context_object_name = 'payments'
    paginate_by = 50
    
    def get_queryset(self):
        queryset = super().get_queryset().select_related('customer', 'entity').order_by('-payment_date')
        method = self.request.GET.get('method')
        if method:
            queryset = queryset.filter(payment_method=method)
        return queryset


class CustomerPaymentCreateView(SessionEntityMixin, LoginRequiredMixin, CreateView):
    """Create a new customer payment."""
    model = CustomerPayment
    form_class = CustomerPaymentForm
    template_name = 'ar/customerpayment_form.html'
    success_url = reverse_lazy('ar:payment_list')
    
    def post(self, request, *args, **kwargs):
        """Handle form submission."""
        print("\n" + "="*80)
        print("PAYMENT FORM DATA RECEIVED:")
        print("="*80)
        for key, value in request.POST.items():
            print(f"  {key}: {value}")
        print("="*80 + "\n")
        return super().post(request, *args, **kwargs)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Get session entity instead of first active entity
        entity_id = self.request.session.get('selected_entity_id')
        entity = Entity.objects.filter(id=entity_id, is_active=True).first()
        if entity:
            kwargs['initial'] = {'entity': entity}
        return kwargs
    
    def form_valid(self, form):
        # Use session entity
        entity_id = self.request.session.get('selected_entity_id')
        entity = Entity.objects.filter(id=entity_id, is_active=True).first()
        
        payment = form.save(commit=False)
        payment.entity = entity
        payment.created_by = self.request.user
        
        # Generate payment number if not provided
        if not payment.payment_number:
            last_payment = CustomerPayment.objects.filter(entity=entity).order_by('-id').first()
            payment_count = last_payment.id if last_payment else 0
            payment.payment_number = f"PAY-{timezone.now().strftime('%Y%m%d')}-{payment_count + 1:04d}"
        
        try:
            payment.save()
            print(f"✓ SUCCESS: Payment recorded!")
            print(f"  ID: {payment.id}")
            print(f"  Payment Number: {payment.payment_number}")
            print(f"  Amount: {payment.payment_amount}")
            
            # Create reconciliation if invoice is specified
            if payment.invoice:
                ARReconciliation.objects.create(
                    entity=entity,
                    invoice=payment.invoice,
                    payment=payment,
                    matched_amount=payment.payment_amount,
                    reconciliation_date=payment.payment_date,
                    is_matched=True
                )
                
                # Update invoice amount_paid
                invoice = payment.invoice
                invoice.amount_paid += payment.payment_amount
                
                # Update invoice status
                if invoice.amount_paid >= invoice.total_amount:
                    invoice.status = 'PAID'
                elif invoice.amount_paid > 0:
                    invoice.status = 'PARTIALLY_PAID'
                
                invoice.save()
                print(f"✓ Invoice {invoice.invoice_number} updated")
                print(f"  Amount Paid: {invoice.amount_paid}")
                print(f"  Status: {invoice.status}")
            
            AuditLog.objects.create(
                entity=entity,
                user=self.request.user.username,
                action='CREATE',
                model_name='CustomerPayment',
                object_id=payment.id,
                description=f'Recorded customer payment: {payment.payment_number}'
            )
            
            messages.success(self.request, f'Customer payment {payment.payment_number} recorded successfully.')
            print(f"✓ Message added to queue")
            response = super().form_valid(form)
            print(f"✓ Redirecting to: {self.success_url}")
            return response
        except Exception as e:
            print(f"✗ ERROR saving payment: {str(e)}")
            import traceback
            traceback.print_exc()
            messages.error(self.request, f'Error recording payment: {str(e)}')
            return self.form_invalid(form)
    
    def form_invalid(self, form):
        """Handle form validation errors with detailed feedback."""
        print("\n" + "="*80)
        print("PAYMENT FORM VALIDATION FAILED")
        print("="*80)
        print(f"Form errors: {form.errors}")
        print(f"Form non-field errors: {form.non_field_errors()}")
        print("="*80 + "\n")
        
        error_count = 0
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"❌ {field.upper()}: {error}")
                error_count += 1
                print(f"  ❌ {field}: {error}")
        
        if form.non_field_errors():
            for error in form.non_field_errors():
                messages.error(self.request, f"❌ Form Error: {error}")
                error_count += 1
                print(f"  ❌ General: {error}")
        
        print(f"Total errors: {error_count}\n")
        return super().form_invalid(form)


class CustomerPaymentDetailView(SessionEntityMixin, LoginRequiredMixin, DetailView):
    """Detail view for customer payment."""
    model = CustomerPayment
    template_name = 'ar/customerpayment_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reconciliations'] = self.object.reconciliations.all()
        return context


class ARAgingReportView(SessionEntityMixin, LoginRequiredMixin, TemplateView):
    """Generate AR aging report."""
    template_name = 'ar/ar_aging_report.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get session entity
        entity_id = self.request.session.get('selected_entity_id')
        entity = Entity.objects.filter(id=entity_id, is_active=True).first()
        
        today = timezone.now().date()
        
        # Get all unpaid invoices - filtered by entity
        unpaid_invoices = CustomerInvoice.objects.filter(
            entity=entity,
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
