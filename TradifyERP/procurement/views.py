from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from accounting.mixins import SessionEntityMixin
from django.urls import reverse_lazy
from django.db.models import Q, Sum, F
from django.utils import timezone

from .models import (
    PurchaseOrder, POLineItem, GoodsReceipt, GoodsReceiptLineItem,
    ThreeWayMatching, RequestForQuotation, VendorQuotation
)
from .forms import (
    PurchaseOrderForm, POLineItemForm, GoodsReceiptForm, GoodsReceiptLineItemForm,
    RequestForQuotationForm, VendorQuotationForm, ThreeWayMatchingForm,
    RawMaterialPurchaseOrderForm, RawMaterialPOLineItemForm
)
from .gl_integration import create_po_gl_entries, create_gr_gl_entries, create_po_payment_gl_entries, reverse_po_gl_entries


class ProcurementDashboardView(SessionEntityMixin, LoginRequiredMixin, TemplateView):
    """Procurement Module Dashboard - overview of POs, receipts, and RFQs."""
    template_name = 'procurement/dashboard.html'
    login_url = 'login'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get PO statistics
        pos_total = PurchaseOrder.objects.count()
        pos_draft = PurchaseOrder.objects.filter(status='DRAFT').count()
        pos_received = PurchaseOrder.objects.filter(status='RECEIVED').count()
        pos_pending_receipt = PurchaseOrder.objects.filter(status__in=['SENT', 'ACKNOWLEDGED']).count()
        
        # Outstanding commitments
        outstanding_po = PurchaseOrder.objects.filter(
            status__in=['DRAFT', 'SENT', 'ACKNOWLEDGED', 'PARTIAL']
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        
        # Goods receipt statistics
        receipts_total = GoodsReceipt.objects.count()
        receipts_pending = GoodsReceipt.objects.filter(status='PENDING').count()
        
        # RFQ statistics
        rfqs_active = RequestForQuotation.objects.filter(awarded_to__isnull=True).count()
        rfqs_awarded = RequestForQuotation.objects.filter(awarded_to__isnull=False).count()
        
        # 3-Way Matching
        matching_discrepancies = ThreeWayMatching.objects.filter(resolved=False).count()
        
        # Recent POs
        recent_pos = PurchaseOrder.objects.order_by('-po_date')[:10]
        
        # Recent Receipts
        recent_receipts = GoodsReceipt.objects.order_by('-receipt_date')[:10]
        
        context.update({
            'pos_total': pos_total,
            'pos_draft': pos_draft,
            'pos_received': pos_received,
            'pos_pending_receipt': pos_pending_receipt,
            'outstanding_po': outstanding_po,
            'receipts_total': receipts_total,
            'receipts_pending': receipts_pending,
            'rfqs_active': rfqs_active,
            'rfqs_awarded': rfqs_awarded,
            'matching_discrepancies': matching_discrepancies,
            'recent_pos': recent_pos,
            'recent_receipts': recent_receipts,
        })
        
        return context


class PurchaseOrderListView(SessionEntityMixin, LoginRequiredMixin, ListView):
    """List all purchase orders with filtering and search."""
    model = PurchaseOrder
    template_name = 'procurement/purchaseorder_list.html'
    context_object_name = 'purchase_orders'
    paginate_by = 20
    login_url = 'login'
    
    def get_queryset(self):
        queryset = PurchaseOrder.objects.all().select_related('vendor', 'entity').order_by('-po_date')
        
        # Search by PO number or vendor name
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(po_number__icontains=search) | 
                Q(vendor__name__icontains=search)
            )
        
        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Filter by entity
        entity = self.request.GET.get('entity')
        if entity:
            queryset = queryset.filter(entity_id=entity)
        
        return queryset


class PurchaseOrderDetailView(SessionEntityMixin, LoginRequiredMixin, DetailView):
    """Display detailed view of a purchase order with line items."""
    model = PurchaseOrder
    template_name = 'procurement/purchaseorder_detail.html'
    context_object_name = 'purchase_order'
    login_url = 'login'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        po = self.get_object()
        context['line_items'] = po.polineitem_set.all()
        context['receipts'] = po.goodsreceipt_set.all()
        return context


class PurchaseOrderCreateView(SessionEntityMixin, LoginRequiredMixin, CreateView):
    """Create a new purchase order."""
    model = PurchaseOrder
    form_class = PurchaseOrderForm
    template_name = 'procurement/purchaseorder_form.html'
    success_url = reverse_lazy('procurement:po_list')
    login_url = 'login'


class PurchaseOrderUpdateView(SessionEntityMixin, LoginRequiredMixin, UpdateView):
    """Update an existing purchase order."""
    model = PurchaseOrder
    form_class = PurchaseOrderForm
    template_name = 'procurement/purchaseorder_form.html'
    success_url = reverse_lazy('procurement:po_list')
    login_url = 'login'
    
    def form_valid(self, form):
        old_instance = self.get_object()
        old_status = old_instance.status
        
        instance = form.save(commit=True)
        new_status = instance.status
        
        # If status changed to RECEIVED, create GL entries
        if old_status != 'RECEIVED' and new_status == 'RECEIVED':
            create_po_gl_entries(instance)
        
        # If PO was cancelled, reverse GL entries
        if old_status != 'CANCELLED' and new_status == 'CANCELLED':
            reverse_po_gl_entries(instance)
        
        return redirect(self.success_url)


class PurchaseOrderApproveView(SessionEntityMixin, LoginRequiredMixin, UpdateView):
    """Approve a purchase order."""
    model = PurchaseOrder
    fields = []
    template_name = 'procurement/purchaseorder_confirm_approve.html'
    success_url = reverse_lazy('procurement:po_list')
    login_url = 'login'
    
    def form_valid(self, form):
        po = self.get_object()
        po.status = 'SENT'
        return super().form_valid(form)


class GoodsReceiptListView(SessionEntityMixin, LoginRequiredMixin, ListView):
    """List all goods receipts with filtering."""
    model = GoodsReceipt
    template_name = 'procurement/goodsreceipt_list.html'
    context_object_name = 'receipts'
    paginate_by = 20
    login_url = 'login'
    
    def get_queryset(self):
        queryset = GoodsReceipt.objects.all().select_related('po').order_by('-receipt_date')
        
        # Search by receipt number or tracking number
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(receipt_number__icontains=search) | 
                Q(tracking_number__icontains=search)
            )
        
        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset


class GoodsReceiptDetailView(SessionEntityMixin, LoginRequiredMixin, DetailView):
    """Display detailed view of a goods receipt."""
    model = GoodsReceipt
    template_name = 'procurement/goodsreceipt_detail.html'
    context_object_name = 'goods_receipt'
    login_url = 'login'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        receipt = self.get_object()
        context['receipt_items'] = receipt.goodsreceiptlineitem_set.all()
        return context


class GoodsReceiptCreateView(SessionEntityMixin, LoginRequiredMixin, CreateView):
    """Create a new goods receipt."""
    model = GoodsReceipt
    form_class = GoodsReceiptForm
    template_name = 'procurement/goodsreceipt_form.html'
    success_url = reverse_lazy('procurement:receipt_list')
    login_url = 'login'
    
    def form_valid(self, form):
        instance = form.save(commit=True)
        
        # Create GL entries if goods receipt is RECEIVED
        if instance.status == 'RECEIVED':
            create_gr_gl_entries(instance)
        
        return redirect(self.success_url)


class GoodsReceiptUpdateView(SessionEntityMixin, LoginRequiredMixin, UpdateView):
    """Update an existing goods receipt."""
    model = GoodsReceipt
    form_class = GoodsReceiptForm
    template_name = 'procurement/goodsreceipt_form.html'
    success_url = reverse_lazy('procurement:receipt_list')
    login_url = 'login'
    
    def form_valid(self, form):
        old_instance = self.get_object()
        old_status = old_instance.status
        
        instance = form.save(commit=True)
        new_status = instance.status
        
        # If status changed to RECEIVED, create GL entries
        if old_status != 'RECEIVED' and new_status == 'RECEIVED':
            create_gr_gl_entries(instance)
        
        return redirect(self.success_url)


class RequestForQuotationListView(SessionEntityMixin, LoginRequiredMixin, ListView):
    """List all RFQs with filtering."""
    model = RequestForQuotation
    template_name = 'procurement/requestforquotation_list.html'
    context_object_name = 'rfqs'
    paginate_by = 20
    login_url = 'login'
    
    def get_queryset(self):
        queryset = RequestForQuotation.objects.all().select_related('entity', 'awarded_to').order_by('-response_deadline')
        
        # Filter by award status
        award_status = self.request.GET.get('award_status')
        if award_status == 'awarded':
            queryset = queryset.filter(awarded_to__isnull=False)
        elif award_status == 'active':
            queryset = queryset.filter(awarded_to__isnull=True)
        
        return queryset


class RequestForQuotationDetailView(SessionEntityMixin, LoginRequiredMixin, DetailView):
    """Display detailed view of an RFQ with vendor quotations."""
    model = RequestForQuotation
    template_name = 'procurement/requestforquotation_detail.html'
    context_object_name = 'rfq'
    login_url = 'login'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        rfq = self.get_object()
        context['quotations'] = rfq.vendorquotation_set.all().order_by('-score')
        return context


class RequestForQuotationCreateView(SessionEntityMixin, LoginRequiredMixin, CreateView):
    """Create a new RFQ."""
    model = RequestForQuotation
    form_class = RequestForQuotationForm
    template_name = 'procurement/requestforquotation_form.html'
    success_url = reverse_lazy('procurement:rfq_list')
    login_url = 'login'


class VendorQuotationListView(SessionEntityMixin, LoginRequiredMixin, ListView):
    """List all vendor quotations with filtering."""
    model = VendorQuotation
    template_name = 'procurement/vendorquotation_list.html'
    context_object_name = 'quotations'
    paginate_by = 20
    login_url = 'login'
    
    def get_queryset(self):
        queryset = VendorQuotation.objects.all().select_related('rfq', 'vendor').order_by('-quote_date')
        
        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset


class ThreeWayMatchingListView(SessionEntityMixin, LoginRequiredMixin, ListView):
    """List 3-way matching results to identify discrepancies."""
    model = ThreeWayMatching
    template_name = 'procurement/threewymatching_list.html'
    context_object_name = 'matches'
    paginate_by = 20
    login_url = 'login'
    
    def get_queryset(self):
        queryset = ThreeWayMatching.objects.all().select_related('po').order_by('-po__po_date')
        
        # Show only unresolved discrepancies
        discrepancies_only = self.request.GET.get('discrepancies_only')
        if discrepancies_only:
            queryset = queryset.exclude(
                quantity_variance=0,
                price_variance=0
            )
        
        # Filter by resolution status
        resolved = self.request.GET.get('resolved')
        if resolved == 'false':
            queryset = queryset.filter(resolved=False)
        elif resolved == 'true':
            queryset = queryset.filter(resolved=True)
        
        return queryset


class ThreeWayMatchingDetailView(SessionEntityMixin, LoginRequiredMixin, DetailView):
    """Display 3-way matching details and allow resolution."""
    model = ThreeWayMatching
    template_name = 'procurement/threewymatching_detail.html'
    context_object_name = 'match'
    login_url = 'login'


class RawMaterialPurchaseOrderCreateView(SessionEntityMixin, LoginRequiredMixin, CreateView):
    """Create a PO for raw materials with supplier selection."""
    model = PurchaseOrder
    form_class = RawMaterialPurchaseOrderForm
    template_name = 'procurement/rawmaterial_po_form.html'
    success_url = reverse_lazy('procurement:po_list')
    login_url = 'login'
    
    def form_valid(self, form):
        # Set the created_by user
        form.instance.created_by = self.request.user
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Create Raw Material Purchase Order'
        context['form_type'] = 'raw_material'
        return context


class RawMaterialPOLineItemAddView(SessionEntityMixin, LoginRequiredMixin, CreateView):
    """Add raw material line items to a PO."""
    model = POLineItem
    form_class = RawMaterialPOLineItemForm
    template_name = 'procurement/rawmaterial_polineitem_form.html'
    login_url = 'login'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        po_id = self.kwargs.get('po_id')
        context['po'] = PurchaseOrder.objects.get(id=po_id)
        return context
    
    def form_valid(self, form):
        po_id = self.kwargs.get('po_id')
        form.instance.po = PurchaseOrder.objects.get(id=po_id)
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('procurement:po_detail', kwargs={'pk': self.kwargs.get('po_id')})

