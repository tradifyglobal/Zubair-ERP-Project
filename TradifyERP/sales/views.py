"""
Sales Module Views
Complete CRUD operations with RBAC and multi-entity support.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.urls import reverse_lazy
from django.db.models import Q, Sum, Count
from django.middleware.csrf import get_token
from decimal import Decimal

from accounting.role_models import UserRole
from accounting.models import Entity
from .models import Customer, SalesOrder, SalesOrderLine, Invoice
from .forms import CustomerForm, SalesOrderForm, SalesOrderLineForm, InvoiceForm
from .gl_integration import create_invoice_gl_entries, create_payment_gl_entries, reverse_invoice_gl_entries


# ==================== Utility Functions ====================

def get_user_entities(user):
    """Get entities accessible to user based on UserRole."""
    return UserRole.objects.filter(
        user=user,
        is_active=True
    ).values_list('entity_id', flat=True)


def get_filtered_queryset(model, user, base_queryset=None):
    """Filter queryset by user's accessible entities."""
    if base_queryset is None:
        base_queryset = model.objects.all()
    
    user_entities = get_user_entities(user)
    return base_queryset.filter(entity_id__in=user_entities)


# ==================== Customer Views ====================

@method_decorator(csrf_protect, name='dispatch')
class CustomerListView(LoginRequiredMixin, ListView):
    model = Customer
    template_name = 'sales/customer_list.html'
    context_object_name = 'customers'
    paginate_by = 25
    
    def get_queryset(self):
        qs = get_filtered_queryset(Customer, self.request.user)
        
        search = self.request.GET.get('search', '')
        if search:
            qs = qs.filter(Q(customer_name__icontains=search) | Q(customer_code__icontains=search))
        
        status = self.request.GET.get('status', '')
        if status:
            qs = qs.filter(status=status)
        
        return qs.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['statuses'] = Customer.STATUS
        context['csrf_token'] = get_token(self.request)
        return context


@method_decorator(csrf_protect, name='dispatch')
class CustomerCreateView(LoginRequiredMixin, CreateView):
    model = Customer
    form_class = CustomerForm
    template_name = 'sales/customer_form.html'
    success_url = reverse_lazy('sales:customer_list')
    
    def form_valid(self, form):
        user_entities = list(get_user_entities(self.request.user))
        if not user_entities:
            return redirect('sales:customer_list')
        
        instance = form.save(commit=False)
        instance.entity_id = user_entities[0]
        instance.created_by = self.request.user
        instance.save()
        
        return redirect(self.success_url)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['csrf_token'] = get_token(self.request)
        return context


@method_decorator(csrf_protect, name='dispatch')
class CustomerUpdateView(LoginRequiredMixin, UpdateView):
    model = Customer
    form_class = CustomerForm
    template_name = 'sales/customer_form.html'
    success_url = reverse_lazy('sales:customer_list')
    
    def get_queryset(self):
        return get_filtered_queryset(Customer, self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['csrf_token'] = get_token(self.request)
        return context


@method_decorator(csrf_protect, name='dispatch')
class CustomerDeleteView(LoginRequiredMixin, DeleteView):
    model = Customer
    template_name = 'sales/customer_confirm_delete.html'
    success_url = reverse_lazy('sales:customer_list')
    
    def get_queryset(self):
        return get_filtered_queryset(Customer, self.request.user)


# ==================== Sales Order Views ====================

@method_decorator(csrf_protect, name='dispatch')
class SalesOrderListView(LoginRequiredMixin, ListView):
    model = SalesOrder
    template_name = 'sales/salesorder_list.html'
    context_object_name = 'sales_orders'
    paginate_by = 25
    
    def get_queryset(self):
        qs = get_filtered_queryset(SalesOrder, self.request.user)
        
        search = self.request.GET.get('search', '')
        if search:
            qs = qs.filter(Q(so_number__icontains=search) | Q(customer__customer_name__icontains=search))
        
        status = self.request.GET.get('status', '')
        if status:
            qs = qs.filter(status=status)
        
        return qs.order_by('-order_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['statuses'] = SalesOrder.STATUS_CHOICES
        context['csrf_token'] = get_token(self.request)
        return context


@method_decorator(csrf_protect, name='dispatch')
class SalesOrderCreateView(LoginRequiredMixin, CreateView):
    model = SalesOrder
    form_class = SalesOrderForm
    template_name = 'sales/salesorder_form.html'
    success_url = reverse_lazy('sales:salesorder_list')
    
    def form_valid(self, form):
        user_entities = list(get_user_entities(self.request.user))
        if not user_entities:
            return redirect('sales:salesorder_list')
        
        instance = form.save(commit=False)
        instance.entity_id = user_entities[0]
        instance.created_by = self.request.user
        instance.save()
        
        return redirect(self.success_url)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['csrf_token'] = get_token(self.request)
        return context


@method_decorator(csrf_protect, name='dispatch')
class SalesOrderUpdateView(LoginRequiredMixin, UpdateView):
    model = SalesOrder
    form_class = SalesOrderForm
    template_name = 'sales/salesorder_form.html'
    success_url = reverse_lazy('sales:salesorder_list')
    
    def get_queryset(self):
        return get_filtered_queryset(SalesOrder, self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['csrf_token'] = get_token(self.request)
        return context


@method_decorator(csrf_protect, name='dispatch')
class SalesOrderDeleteView(LoginRequiredMixin, DeleteView):
    model = SalesOrder
    template_name = 'sales/salesorder_confirm_delete.html'
    success_url = reverse_lazy('sales:salesorder_list')
    
    def get_queryset(self):
        return get_filtered_queryset(SalesOrder, self.request.user)


# ==================== Invoice Views ====================

@method_decorator(csrf_protect, name='dispatch')
class InvoiceListView(LoginRequiredMixin, ListView):
    model = Invoice
    template_name = 'sales/invoice_list.html'
    context_object_name = 'invoices'
    paginate_by = 25
    
    def get_queryset(self):
        qs = get_filtered_queryset(Invoice, self.request.user)
        
        search = self.request.GET.get('search', '')
        if search:
            qs = qs.filter(Q(invoice_number__icontains=search) | Q(customer__customer_name__icontains=search))
        
        status = self.request.GET.get('status', '')
        if status:
            qs = qs.filter(status=status)
        
        return qs.order_by('-invoice_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['statuses'] = Invoice.INVOICE_STATUS
        context['csrf_token'] = get_token(self.request)
        return context


@method_decorator(csrf_protect, name='dispatch')
class InvoiceCreateView(LoginRequiredMixin, CreateView):
    model = Invoice
    form_class = InvoiceForm
    template_name = 'sales/invoice_form.html'
    success_url = reverse_lazy('sales:invoice_list')
    
    def form_valid(self, form):
        user_entities = list(get_user_entities(self.request.user))
        if not user_entities:
            return redirect('sales:invoice_list')
        
        instance = form.save(commit=False)
        instance.entity_id = user_entities[0]
        instance.issued_by = self.request.user
        
        # Copy amounts from sales order
        so = instance.sales_order
        instance.customer = so.customer
        instance.subtotal = so.subtotal
        instance.tax_amount = so.tax_amount
        instance.total_amount = so.total_amount
        
        instance.save()
        
        # Create GL entries if invoice is ISSUED (revenue recognition)
        if instance.status == 'ISSUED':
            create_invoice_gl_entries(instance)
        
        return redirect(self.success_url)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['csrf_token'] = get_token(self.request)
        return context


@method_decorator(csrf_protect, name='dispatch')
class InvoiceUpdateView(LoginRequiredMixin, UpdateView):
    model = Invoice
    form_class = InvoiceForm
    template_name = 'sales/invoice_form.html'
    success_url = reverse_lazy('sales:invoice_list')
    
    def get_queryset(self):
        return get_filtered_queryset(Invoice, self.request.user)
    
    def form_valid(self, form):
        old_instance = self.get_object()
        old_amount_paid = old_instance.amount_paid
        
        instance = form.save(commit=False)
        instance.save()
        
        # Handle GL entries based on status changes and payments
        new_status = instance.status
        old_status = old_instance.status
        new_amount_paid = instance.amount_paid
        
        # If status changed to ISSUED, create revenue GL entries
        if old_status != 'ISSUED' and new_status == 'ISSUED':
            create_invoice_gl_entries(instance)
        
        # If payment received, create payment GL entries
        if new_amount_paid > old_amount_paid:
            payment_amount = new_amount_paid - old_amount_paid
            create_payment_gl_entries(instance, payment_amount)
        
        # If invoice was cancelled, reverse GL entries
        if old_status != 'CANCELLED' and new_status == 'CANCELLED':
            reverse_invoice_gl_entries(instance)
        
        return redirect(self.success_url)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['csrf_token'] = get_token(self.request)
        return context


@method_decorator(csrf_protect, name='dispatch')
class InvoiceDeleteView(LoginRequiredMixin, DeleteView):
    model = Invoice
    template_name = 'sales/invoice_confirm_delete.html'
    success_url = reverse_lazy('sales:invoice_list')
    
    def get_queryset(self):
        return get_filtered_queryset(Invoice, self.request.user)
    
    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Reverse GL entries if invoice was already posted
        if instance.status in ['ISSUED', 'PAID', 'PARTIAL', 'OVERDUE']:
            reverse_invoice_gl_entries(instance)
        
        return super().delete(request, *args, **kwargs)


# ==================== Sales Dashboard ====================

@method_decorator(csrf_protect, name='dispatch')
class SalesDashboardView(LoginRequiredMixin, TemplateView):
    """Sales dashboard with KPIs and metrics."""
    template_name = 'sales/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_entities = get_user_entities(self.request.user)
        
        # Sales metrics
        total_customers = Customer.objects.filter(entity_id__in=user_entities).count()
        active_customers = Customer.objects.filter(entity_id__in=user_entities, status='ACTIVE').count()
        
        total_orders = SalesOrder.objects.filter(entity_id__in=user_entities).count()
        pending_orders = SalesOrder.objects.filter(
            entity_id__in=user_entities,
            status__in=['DRAFT', 'CONFIRMED', 'PROCESSING']
        ).count()
        shipped_orders = SalesOrder.objects.filter(
            entity_id__in=user_entities,
            status='SHIPPED'
        ).count()
        
        # Revenue metrics
        total_revenue = SalesOrder.objects.filter(
            entity_id__in=user_entities,
            status__in=['INVOICED', 'DELIVERED']
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
        
        # Invoice metrics
        total_invoices = Invoice.objects.filter(entity_id__in=user_entities).count()
        paid_invoices = Invoice.objects.filter(entity_id__in=user_entities, status='PAID').count()
        overdue_invoices = Invoice.objects.filter(entity_id__in=user_entities, status='OVERDUE').count()
        
        total_outstanding = Invoice.objects.filter(
            entity_id__in=user_entities,
            status__in=['ISSUED', 'PARTIAL', 'OVERDUE']
        ).aggregate(total=Sum('total_amount') - Sum('amount_paid'))['total'] or Decimal('0.00')
        
        context = {
            'total_customers': total_customers,
            'active_customers': active_customers,
            'total_orders': total_orders,
            'pending_orders': pending_orders,
            'shipped_orders': shipped_orders,
            'total_revenue': total_revenue,
            'total_invoices': total_invoices,
            'paid_invoices': paid_invoices,
            'overdue_invoices': overdue_invoices,
            'total_outstanding': total_outstanding,
            'csrf_token': get_token(self.request),
        }
        
        return context
