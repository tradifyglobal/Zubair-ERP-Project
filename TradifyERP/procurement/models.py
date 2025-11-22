from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal
from django.utils import timezone
from accounting.models import Entity, Account, LedgerEntry, Vendor
from inventory.models import Product
from ap.models import VendorBill


class PurchaseOrder(models.Model):
    """Purchase Order (PO) - request to buy goods/services from vendor"""
    
    PO_STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('SENT', 'Sent to Vendor'),
        ('ACKNOWLEDGED', 'Acknowledged'),
        ('PARTIAL', 'Partially Received'),
        ('RECEIVED', 'Fully Received'),
        ('INVOICED', 'Invoiced'),
        ('PAID', 'Paid'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    # Reference
    po_number = models.CharField(max_length=50, unique=True, db_index=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.PROTECT, related_name='purchase_orders')
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE, related_name='purchase_orders')
    
    # Dates
    po_date = models.DateField(auto_now_add=True, db_index=True)
    expected_delivery_date = models.DateField(null=True, blank=True)
    actual_delivery_date = models.DateField(null=True, blank=True)
    
    # Amounts
    subtotal = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2)
    
    # Receiving Tracking
    amount_received = models.DecimalField(max_digits=15, decimal_places=2, default=0)  # Sum of goods receipts
    amount_invoiced = models.DecimalField(max_digits=15, decimal_places=2, default=0)  # Sum of matched invoices
    
    # Status
    status = models.CharField(max_length=20, choices=PO_STATUS_CHOICES, default='DRAFT', db_index=True)
    
    # Details
    description = models.TextField(blank=True, null=True)
    shipping_address = models.TextField(blank=True, null=True)
    payment_terms = models.CharField(max_length=100, blank=True, null=True)  # e.g., "Net 30"
    
    # Approval
    is_approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_pos')
    
    # System Fields
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_pos')
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-po_date']
        indexes = [
            models.Index(fields=['vendor', 'entity']),
            models.Index(fields=['status']),
            models.Index(fields=['expected_delivery_date']),
        ]
    
    def __str__(self):
        return f"{self.po_number} - {self.vendor.name} - {self.total_amount}"


class POLineItem(models.Model):
    """Line items on a Purchase Order"""
    
    po = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='line_items')
    
    # Item Info
    description = models.CharField(max_length=255)
    quantity_ordered = models.DecimalField(max_digits=10, decimal_places=2)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    line_total = models.DecimalField(max_digits=15, decimal_places=2)
    
    # Tracking
    quantity_received = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    quantity_invoiced = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Item Reference
    inventory_product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, related_name='po_line_items')
    
    # GL Coding
    expense_account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, blank=True, related_name='po_line_items')
    cost_center = models.CharField(max_length=50, blank=True, null=True)
    
    # Notes
    notes = models.TextField(blank=True, null=True)
    
    # Tax
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    created_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.po.po_number} - {self.description}"


class GoodsReceipt(models.Model):
    """Goods Receipt - records receipt of goods from PO"""
    
    RECEIPT_STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('RECEIVED', 'Received'),
        ('INSPECTED', 'Inspected'),
        ('ACCEPTED', 'Accepted'),
        ('REJECTED', 'Rejected'),
    ]
    
    # Reference
    receipt_number = models.CharField(max_length=50, unique=True, db_index=True)
    po = models.ForeignKey(PurchaseOrder, on_delete=models.PROTECT, related_name='receipts')
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE, related_name='goods_receipts')
    
    # Dates
    receipt_date = models.DateField(auto_now_add=True, db_index=True)
    inspection_date = models.DateField(null=True, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=RECEIPT_STATUS_CHOICES, default='DRAFT', db_index=True)
    
    # Details
    carrier = models.CharField(max_length=100, blank=True, null=True)
    tracking_number = models.CharField(max_length=100, blank=True, null=True)
    received_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='received_goods')
    
    # GL Integration
    gl_entry = models.OneToOneField(LedgerEntry, on_delete=models.SET_NULL, null=True, blank=True, related_name='goods_receipt')
    
    created_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-receipt_date']
    
    def __str__(self):
        return f"{self.receipt_number} - {self.po.po_number}"


class GoodsReceiptLineItem(models.Model):
    """Line items received in a Goods Receipt"""
    
    receipt = models.ForeignKey(GoodsReceipt, on_delete=models.CASCADE, related_name='line_items')
    po_line = models.ForeignKey(POLineItem, on_delete=models.PROTECT, related_name='receipts')
    
    # Quantities
    quantity_received = models.DecimalField(max_digits=10, decimal_places=2)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    line_total = models.DecimalField(max_digits=15, decimal_places=2)
    
    # Quality
    quantity_accepted = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    quantity_rejected = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    rejection_reason = models.TextField(blank=True, null=True)
    
    created_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.receipt.receipt_number} - {self.po_line.description}"


class ThreeWayMatching(models.Model):
    """3-Way Matching: PO vs. Receipt vs. Invoice"""
    
    MATCH_STATUS_CHOICES = [
        ('UNMATCHED', 'Unmatched'),
        ('PARTIAL_MATCH', 'Partially Matched'),
        ('MATCHED', 'Fully Matched'),
        ('DISCREPANCY', 'Discrepancy'),
    ]
    
    po = models.OneToOneField(PurchaseOrder, on_delete=models.CASCADE, related_name='three_way_match')
    
    # Matching
    po_line = models.ForeignKey(POLineItem, on_delete=models.PROTECT)
    receipt_line = models.ForeignKey(GoodsReceiptLineItem, on_delete=models.SET_NULL, null=True, blank=True, related_name='matches')
    bill_line = models.ForeignKey('ap.VendorBillLineItem', on_delete=models.SET_NULL, null=True, blank=True, related_name='matches')
    
    # Amounts
    po_amount = models.DecimalField(max_digits=15, decimal_places=2)
    receipt_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    invoice_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Tolerances (percentage)
    quantity_variance = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    price_variance = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Status
    status = models.CharField(max_length=20, choices=MATCH_STATUS_CHOICES, default='UNMATCHED', db_index=True)
    
    # Notes
    discrepancy_notes = models.TextField(blank=True, null=True)
    resolved = models.BooleanField(default=False)
    resolution_notes = models.TextField(blank=True, null=True)
    
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"3-Way Match - {self.po.po_number}"


class RequestForQuotation(models.Model):
    """Request for Quotation (RFQ) - send to vendors for pricing"""
    
    RFQ_STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('SENT', 'Sent to Vendors'),
        ('RESPONSES', 'Responses Received'),
        ('EVALUATED', 'Evaluated'),
        ('AWARDED', 'PO Awarded'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    # Reference
    rfq_number = models.CharField(max_length=50, unique=True, db_index=True)
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE, related_name='rfqs')
    
    # Vendors
    vendors = models.ManyToManyField(Vendor, related_name='rfqs')
    
    # Dates
    rfq_date = models.DateField(auto_now_add=True, db_index=True)
    response_deadline = models.DateField()
    award_date = models.DateField(null=True, blank=True)
    
    # Details
    description = models.TextField()
    status = models.CharField(max_length=20, choices=RFQ_STATUS_CHOICES, default='DRAFT', db_index=True)
    
    # Award
    awarded_to = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True, blank=True, related_name='awarded_rfqs')
    award_notes = models.TextField(blank=True, null=True)
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_rfqs')
    created_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-rfq_date']
    
    def __str__(self):
        return f"{self.rfq_number} - {self.entity.name}"


class VendorQuotation(models.Model):
    """Vendor responses to RFQ"""
    
    QUOTATION_STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('SUBMITTED', 'Submitted'),
        ('EVALUATED', 'Evaluated'),
        ('SELECTED', 'Selected'),
        ('REJECTED', 'Rejected'),
    ]
    
    rfq = models.ForeignKey(RequestForQuotation, on_delete=models.CASCADE, related_name='quotations')
    vendor = models.ForeignKey(Vendor, on_delete=models.PROTECT, related_name='quotations')
    
    # Quote Details
    quote_number = models.CharField(max_length=50)
    quote_date = models.DateField()
    quote_amount = models.DecimalField(max_digits=15, decimal_places=2)
    
    # Terms
    delivery_days = models.IntegerField()  # Days to deliver
    payment_terms = models.CharField(max_length=100, blank=True, null=True)
    warranty_period = models.CharField(max_length=100, blank=True, null=True)
    
    # Status
    status = models.CharField(max_length=20, choices=QUOTATION_STATUS_CHOICES, default='DRAFT', db_index=True)
    
    # Evaluation
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # 0-100
    evaluation_notes = models.TextField(blank=True, null=True)
    
    submitted_date = models.DateTimeField(null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['rfq', 'vendor']
    
    def __str__(self):
        return f"Quote {self.quote_number} - {self.vendor.name} - {self.quote_amount}"


class ProcurementSettings(models.Model):
    """Procurement module settings per entity"""
    
    entity = models.OneToOneField(Entity, on_delete=models.CASCADE, related_name='procurement_settings')
    
    # Policies
    require_rfq_for_po = models.BooleanField(default=False)  # Require RFQ before PO
    require_po_for_receipt = models.BooleanField(default=True)  # Require PO before goods receipt
    enable_3way_matching = models.BooleanField(default=False)  # Enable PO/Receipt/Invoice 3-way match
    
    # Tolerances
    quantity_variance_tolerance = models.DecimalField(max_digits=5, decimal_places=2, default=5)  # %
    price_variance_tolerance = models.DecimalField(max_digits=5, decimal_places=2, default=10)  # %
    
    # Approval
    require_po_approval = models.BooleanField(default=True)
    po_approval_threshold = models.DecimalField(max_digits=15, decimal_places=2, default=0)  # Amount threshold for approval
    
    # Defaults
    default_payment_terms_days = models.IntegerField(default=30)
    auto_receipt_on_delivery = models.BooleanField(default=False)
    
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Procurement Settings - {self.entity.name}"
