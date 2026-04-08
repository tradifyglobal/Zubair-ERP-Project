"""
Procure-to-Pay (P2P) Dashboard Views

Displays complete procurement workflow with accounting integration:
1. Purchase Orders (no GL entries)
2. Goods Receipts (GL: DR Inventory / CR GR/IR)
3. Vendor Invoices (GL: DR GR/IR / CR AP)
4. Vendor Payments (GL: DR AP / CR Bank)
"""

from django.shortcuts import render
from django.views.generic import ListView, DetailView
from django.http import JsonResponse
from django.db.models import Sum, Count, F, Case, When, Value
from django.db.models import DecimalField, Q
from django.utils.timezone import now
from procurement.models import PurchaseOrder, GoodsReceipt, GoodsReceiptLineItem
from ap.models import VendorBill, VendorPayment
from accounting.models import LedgerEntry, Entity
import json
from decimal import Decimal


class P2PDashboardView(ListView):
    """
    Main P2P Dashboard showing pipeline of all procurement documents
    with their GL posting status and amounts.
    """
    template_name = 'procurement/p2p_dashboard.html'
    context_object_name = 'dashboard_data'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get all entities for filter
        context['entities'] = Entity.objects.all()
        
        # Get selected entity from request
        selected_entity_id = self.request.GET.get('entity_id')
        
        # Base querysets
        po_qs = PurchaseOrder.objects.all()
        grn_qs = GoodsReceipt.objects.all()
        invoice_qs = VendorBill.objects.all()
        payment_qs = VendorPayment.objects.all()
        
        # Filter by entity if selected
        if selected_entity_id:
            context['selected_entity_id'] = int(selected_entity_id)
            po_qs = po_qs.filter(entity_id=selected_entity_id)
            grn_qs = grn_qs.filter(entity_id=selected_entity_id)
            invoice_qs = invoice_qs.filter(entity_id=selected_entity_id)
            payment_qs = payment_qs.filter(entity_id=selected_entity_id)
        
        # Calculate pipeline metrics
        po_total = po_qs.aggregate(total=Sum('total_amount', output_field=DecimalField()))['total'] or Decimal('0')
        
        # Calculate GRN totals using Python (avoid GROUP BY issues)
        grn_total = Decimal('0')
        for grn in grn_qs:
            for item in grn.line_items.all():
                grn_total += Decimal(str(item.quantity_received or 0)) * Decimal(str(item.unit_price or 0))
        
        invoice_total = invoice_qs.aggregate(total=Sum('total_amount', output_field=DecimalField()))['total'] or Decimal('0')
        payment_total = payment_qs.aggregate(total=Sum('payment_amount', output_field=DecimalField()))['total'] or Decimal('0')
        
        # GL Posted amounts (with LedgerEntry)
        grn_gl_posted = Decimal('0')
        for grn in grn_qs.filter(gl_entry__isnull=False):
            for item in grn.line_items.all():
                grn_gl_posted += Decimal(str(item.quantity_received or 0)) * Decimal(str(item.unit_price or 0))
        invoice_gl_posted = invoice_qs.filter(gl_entry__isnull=False).aggregate(total=Sum('total_amount', output_field=DecimalField()))['total'] or Decimal('0')
        payment_gl_posted = payment_qs.filter(gl_entry__isnull=False).aggregate(total=Sum('payment_amount', output_field=DecimalField()))['total'] or Decimal('0')
        
        # Status breakdown
        po_breakdown = {
            'DRAFT': po_qs.filter(status='DRAFT').count(),
            'ISSUED': po_qs.filter(status='ISSUED').count(),
            'RECEIVED': po_qs.filter(status='RECEIVED').count(),
            'CLOSED': po_qs.filter(status='CLOSED').count(),
        }
        
        grn_breakdown = {
            'CREATED': grn_qs.filter(status='CREATED').count(),
            'ACCEPTED': grn_qs.filter(status='ACCEPTED').count(),
            'GL_POSTED': grn_qs.filter(gl_entry__isnull=False).count(),
        }
        
        invoice_breakdown = {
            'DRAFT': invoice_qs.filter(status='DRAFT').count(),
            'APPROVED': invoice_qs.filter(status='APPROVED').count(),
            'MATCHED': invoice_qs.filter(status='MATCHED').count(),
            'GL_POSTED': invoice_qs.filter(gl_entry__isnull=False).count(),
        }
        
        payment_breakdown = {
            'PENDING': payment_qs.filter(is_approved=False).count(),
            'APPROVED': payment_qs.filter(is_approved=True).count(),
            'GL_POSTED': payment_qs.filter(gl_entry__isnull=False).count(),
        }
        
        # Build pipeline data
        context['pipeline'] = {
            'purchase_orders': {
                'total_count': po_qs.count(),
                'total_amount': float(po_total),
                'breakdown': po_breakdown,
                'status': 'No GL entries (commitment only)'
            },
            'goods_receipts': {
                'total_count': grn_qs.count(),
                'total_amount': float(grn_total),
                'gl_posted_count': grn_qs.filter(gl_entry__isnull=False).count(),
                'gl_posted_amount': float(grn_gl_posted),
                'breakdown': grn_breakdown,
                'status': 'GL: DR Inventory / CR GR/IR Clearing'
            },
            'vendor_invoices': {
                'total_count': invoice_qs.count(),
                'total_amount': float(invoice_total),
                'gl_posted_count': invoice_qs.filter(gl_entry__isnull=False).count(),
                'gl_posted_amount': float(invoice_gl_posted),
                'breakdown': invoice_breakdown,
                'status': 'GL: DR GR/IR Clearing / CR Accounts Payable'
            },
            'vendor_payments': {
                'total_count': payment_qs.count(),
                'total_amount': float(payment_total),
                'gl_posted_count': payment_qs.filter(gl_entry__isnull=False).count(),
                'gl_posted_amount': float(payment_gl_posted),
                'breakdown': payment_breakdown,
                'status': 'GL: DR Accounts Payable / CR Bank'
            }
        }
        
        # Recent documents (last 10 of each)
        context['recent_pos'] = po_qs.order_by('-po_date')[:10]
        context['recent_grns'] = grn_qs.order_by('-created_date')[:10]
        context['recent_invoices'] = invoice_qs.order_by('-created_date')[:10]
        context['recent_payments'] = payment_qs.order_by('-created_date')[:10]
        
        return context
    
    def get_queryset(self):
        return []  # Not using queryset in this view


class P2PPipelineAPIView:
    """
    Returns JSON data for P2P pipeline status
    """
    def get(self, request):
        selected_entity_id = request.GET.get('entity_id')
        
        # Filter querysets
        po_qs = PurchaseOrder.objects.all()
        grn_qs = GoodsReceipt.objects.all()
        invoice_qs = VendorBill.objects.all()
        payment_qs = VendorPayment.objects.all()
        
        if selected_entity_id:
            po_qs = po_qs.filter(entity_id=selected_entity_id)
            grn_qs = grn_qs.filter(entity_id=selected_entity_id)
            invoice_qs = invoice_qs.filter(entity_id=selected_entity_id)
            payment_qs = payment_qs.filter(entity_id=selected_entity_id)
        
        # Calculate metrics
        data = {
            'purchase_orders': {
                'total': po_qs.count(),
                'amount': float(po_qs.aggregate(Sum('total_amount'))['total_amount__sum'] or 0),
                'statuses': {
                    'draft': po_qs.filter(status='DRAFT').count(),
                    'issued': po_qs.filter(status='ISSUED').count(),
                    'received': po_qs.filter(status='RECEIVED').count(),
                    'closed': po_qs.filter(status='CLOSED').count(),
                }
            },
            'goods_receipts': {
                'total': grn_qs.count(),
                'gl_posted': grn_qs.filter(gl_entry__isnull=False).count(),
                'pending_gl': grn_qs.filter(status='ACCEPTED', gl_entry__isnull=True).count(),
                'statuses': {
                    'created': grn_qs.filter(status='CREATED').count(),
                    'accepted': grn_qs.filter(status='ACCEPTED').count(),
                }
            },
            'vendor_invoices': {
                'total': invoice_qs.count(),
                'gl_posted': invoice_qs.filter(gl_entry__isnull=False).count(),
                'pending_gl': invoice_qs.filter(status__in=['APPROVED', 'MATCHED'], gl_entry__isnull=True).count(),
                'statuses': {
                    'draft': invoice_qs.filter(status='DRAFT').count(),
                    'approved': invoice_qs.filter(status='APPROVED').count(),
                    'matched': invoice_qs.filter(status='MATCHED').count(),
                }
            },
            'vendor_payments': {
                'total': payment_qs.count(),
                'gl_posted': payment_qs.filter(gl_entry__isnull=False).count(),
                'pending_gl': payment_qs.filter(is_approved=True, gl_entry__isnull=True).count(),
                'statuses': {
                    'pending': payment_qs.filter(is_approved=False).count(),
                    'approved': payment_qs.filter(is_approved=True).count(),
                }
            }
        }
        
        return JsonResponse(data)


class P2PDetailsView(DetailView):
    """
    Shows complete P2P flow for a single Purchase Order:
    - Original PO details
    - Linked GRNs and their GL entries
    - Linked Invoices and their GL entries
    - Linked Payments and their GL entries
    """
    model = PurchaseOrder
    template_name = 'procurement/p2p_details.html'
    context_object_name = 'purchase_order'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        po = self.get_object()
        
        # Get all related documents
        grns = GoodsReceipt.objects.filter(purchase_order=po)
        invoices = VendorBill.objects.filter(purchase_order=po)
        payments = VendorPayment.objects.filter(po_headers=po)
        
        # Calculate totals
        grn_total = sum([li.quantity_received * li.unit_price for g in grns for li in g.line_items.all()])
        invoice_total = invoices.aggregate(Sum('total_amount'))['total_amount__sum'] or Decimal('0')
        payment_total = payments.aggregate(Sum('payment_amount'))['payment_amount__sum'] or Decimal('0')
        
        context.update({
            'grns': grns,
            'invoices': invoices,
            'payments': payments,
            'grn_total': float(grn_total),
            'invoice_total': float(invoice_total),
            'payment_total': float(payment_total),
            'po_total': float(po.total_amount),
            'gl_entries': {
                'grn_entries': LedgerEntry.objects.filter(goods_receipt__in=grns),
                'invoice_entries': LedgerEntry.objects.filter(vendor_bill__in=invoices),
                'payment_entries': LedgerEntry.objects.filter(vendor_payment__in=payments),
            }
        })
        
        return context


def p2p_comparison_view(request):
    """
    Shows side-by-side comparison of:
    - Documents ordered vs received vs invoiced vs paid
    - GL impact at each stage
    - Discrepancies and matching issues
    """
    selected_entity_id = request.GET.get('entity_id')
    
    # Get all POs
    pos = PurchaseOrder.objects.all()
    if selected_entity_id:
        pos = pos.filter(entity_id=selected_entity_id)
    
    # For each PO, calculate coverage
    p2p_data = []
    for po in pos:
        grns = GoodsReceipt.objects.filter(purchase_order=po)
        invoices = VendorBill.objects.filter(purchase_order=po)
        payments = VendorPayment.objects.filter(po_headers=po)
        
        grn_amount = sum([li.quantity_received * li.unit_price for g in grns for li in g.line_items.all()])
        invoice_amount = invoices.aggregate(Sum('total_amount'))['total_amount__sum'] or Decimal('0')
        payment_amount = payments.aggregate(Sum('payment_amount'))['payment_amount__sum'] or Decimal('0')
        
        p2p_data.append({
            'po': po,
            'po_amount': float(po.total_amount),
            'grn_amount': float(grn_amount),
            'invoice_amount': float(invoice_amount),
            'payment_amount': float(payment_amount),
            'grn_count': grns.count(),
            'invoice_count': invoices.count(),
            'payment_count': payments.count(),
            'gl_postings': {
                'grn_gl': grns.filter(gl_entry__isnull=False).count(),
                'invoice_gl': invoices.filter(gl_entry__isnull=False).count(),
                'payment_gl': payments.filter(gl_entry__isnull=False).count(),
            },
            'status': {
                'receipt_status': 'Complete' if grn_amount >= po.total_amount else 'Partial',
                'invoice_status': 'Complete' if invoice_amount >= po.total_amount else 'Partial',
                'payment_status': 'Complete' if payment_amount >= po.total_amount else 'Complete',
                'gl_status': 'Complete' if (grns.filter(gl_entry__isnull=False).count() == grns.count() and
                                           invoices.filter(gl_entry__isnull=False).count() == invoices.count() and
                                           payments.filter(gl_entry__isnull=False).count() == payments.count()) else 'Pending'
            }
        })
    
    context = {
        'p2p_data': p2p_data,
        'entities': Entity.objects.all(),
        'selected_entity_id': selected_entity_id,
    }
    
    return render(request, 'procurement/p2p_comparison.html', context)
