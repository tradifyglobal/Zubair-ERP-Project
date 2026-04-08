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
    
    ITEM_TYPE_CHOICES = [
        ('MATERIAL', 'Raw Material/Product'),
        ('SERVICE', 'Service'),
        ('EQUIPMENT', 'Equipment/Asset'),
        ('FREIGHT', 'Freight/Shipping'),
        ('OTHER', 'Other'),
    ]
    
    po = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='line_items')
    
    # Item Info
    description = models.CharField(max_length=255)
    quantity_ordered = models.DecimalField(max_digits=10, decimal_places=2)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    line_total = models.DecimalField(max_digits=15, decimal_places=2)
    
    # Item Classification
    item_type = models.CharField(max_length=20, choices=ITEM_TYPE_CHOICES, default='MATERIAL')
    
    # Tracking
    quantity_received = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    quantity_invoiced = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Item Reference
    inventory_product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, related_name='po_line_items')
    raw_material = models.ForeignKey('raw_materials.RawMaterial', on_delete=models.SET_NULL, null=True, blank=True, related_name='po_line_items')
    
    # GL Coding
    expense_account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, blank=True, related_name='po_line_items')
    cost_center = models.CharField(max_length=50, blank=True, null=True)
    
    # Notes
    notes = models.TextField(blank=True, null=True)
    
    # Tax
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    tax_type = models.CharField(max_length=50, blank=True, null=True)  # e.g., GST, VAT, Sales Tax
    
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
    
    # Landed Costs (Freight, Duty, Insurance, etc.)
    freight_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    customs_duty = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    insurance_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    handling_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    other_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Tax at Receipt
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_type = models.CharField(max_length=50, blank=True, null=True)
    
    # Cost Variance Tracking
    unit_cost_variance = models.DecimalField(max_digits=12, decimal_places=2, default=0)  # Difference from PO price
    variance_reason = models.CharField(max_length=255, blank=True, null=True)
    
    # GL Account for Cost Allocation
    variance_account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, blank=True, related_name='grn_variances')
    
    created_date = models.DateTimeField(auto_now_add=True)
    
    @property
    def total_landed_cost(self):
        """Calculate total cost including landed costs"""
        return (self.line_total + self.freight_cost + self.customs_duty + 
                self.insurance_cost + self.handling_cost + self.other_cost + self.tax_amount)
    
    @property
    def cost_per_unit_received(self):
        """Cost per unit including landed costs"""
        if self.quantity_received > 0:
            return self.total_landed_cost / self.quantity_received
        return 0
    
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


class PurchaseReturn(models.Model):
    """Purchase Return/Debit Note - Return of goods to supplier"""
    
    RETURN_STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('APPROVED', 'Approved'),
        ('SHIPPED', 'Shipped to Vendor'),
        ('RECEIVED_BY_VENDOR', 'Received by Vendor'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    # Reference
    return_number = models.CharField(max_length=100, unique=True, db_index=True)
    po = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='returns')
    goods_receipt = models.ForeignKey(GoodsReceipt, on_delete=models.PROTECT, null=True, blank=True, related_name='returns')
    vendor = models.ForeignKey(Vendor, on_delete=models.PROTECT)
    entity = models.ForeignKey(Entity, on_delete=models.PROTECT)
    
    # Dates
    return_date = models.DateField(auto_now_add=True)
    expected_vendor_receipt_date = models.DateField(null=True, blank=True)
    vendor_receipt_date = models.DateField(null=True, blank=True)
    
    # Amount
    return_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    return_quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    
    # Return Details
    reason = models.TextField(help_text="Reason for return")
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=RETURN_STATUS_CHOICES, default='DRAFT', db_index=True)
    
    # GL Posting
    gl_entry = models.ForeignKey('accounting.LedgerEntry', on_delete=models.SET_NULL, null=True, blank=True, related_name='purchase_returns')
    gl_posted = models.BooleanField(default=False)
    
    # Tracking
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='purchase_returns_created')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='purchase_returns_approved')
    approved_date = models.DateTimeField(null=True, blank=True)
    
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"PR-{self.return_number} - {self.vendor.vendor_name}"


class DebitNote(models.Model):
    """Debit Note - For supplier adjustments, corrections, etc."""
    
    DEBIT_NOTE_STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('SUBMITTED', 'Submitted to Vendor'),
        ('ACKNOWLEDGED', 'Acknowledged'),
        ('SETTLED', 'Settled in Credit'),
        ('REVERSED', 'Reversed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    DEBIT_NOTE_TYPE_CHOICES = [
        ('PRICE_ADJUSTMENT', 'Price Adjustment'),
        ('QUALITY_DEDUCTION', 'Quality Deduction'),
        ('OVERCHARGE', 'Overcharge Correction'),
        ('RETURN_ALLOWANCE', 'Return Allowance'),
        ('OTHER', 'Other Adjustment'),
    ]
    
    # Reference
    debit_note_number = models.CharField(max_length=100, unique=True, db_index=True)
    po = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='debit_notes')
    vendor_bill = models.ForeignKey('ap.VendorBill', on_delete=models.PROTECT, null=True, blank=True, related_name='debit_notes')
    vendor = models.ForeignKey(Vendor, on_delete=models.PROTECT)
    entity = models.ForeignKey(Entity, on_delete=models.PROTECT)
    
    # Amount & Type
    debit_amount = models.DecimalField(max_digits=15, decimal_places=2)
    debit_type = models.CharField(max_length=20, choices=DEBIT_NOTE_TYPE_CHOICES, default='OTHER')
    
    # Details
    description = models.TextField(help_text="Reason for debit note")
    notes = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=DEBIT_NOTE_STATUS_CHOICES, default='DRAFT', db_index=True)
    
    # GL Posting
    gl_entry = models.ForeignKey('accounting.LedgerEntry', on_delete=models.SET_NULL, null=True, blank=True, related_name='debit_notes')
    gl_posted = models.BooleanField(default=False)
    
    # Settlement
    credited_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    settlement_date = models.DateField(null=True, blank=True)
    
    # Tracking
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='debit_notes_created')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='debit_notes_approved')
    approved_date = models.DateTimeField(null=True, blank=True)
    
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"DN-{self.debit_note_number} - {self.vendor.vendor_name}"


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
