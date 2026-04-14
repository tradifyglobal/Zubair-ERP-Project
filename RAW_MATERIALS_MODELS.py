"""
Raw Materials Management Module - Django Models
For TradifyERP Bio-Plastics Manufacturing

This module handles:
- Raw material master data
- Stock tracking and management
- Purchase ordering
- Supplier management
- Low stock alerts and auto-reordering
- Material cost tracking
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal

# ============================================================================
# 1. RAW MATERIAL CATEGORIES & CHOICES
# ============================================================================

class RawMaterialCategory(models.Model):
    """Categories for grouping raw materials"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Raw Material Category"
        verbose_name_plural = "Raw Material Categories"
        ordering = ['name']
    
    def __str__(self):
        return self.name


# ============================================================================
# 2. SUPPLIER MANAGEMENT
# ============================================================================

class Supplier(models.Model):
    """Supplier master data for raw materials"""
    
    PAYMENT_TERMS_CHOICES = [
        ('CASH', 'Cash on Delivery'),
        ('NET30', 'NET 30 Days'),
        ('NET60', 'NET 60 Days'),
        ('2/10NET30', '2% 10 Days, NET 30'),
        ('PREPAID', 'Prepaid'),
        ('CUSTOM', 'Custom Terms'),
    ]
    
    supplier_code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    contact_person = models.CharField(max_length=255, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    
    # Address
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    
    # Payment & Credit
    payment_terms = models.CharField(max_length=20, choices=PAYMENT_TERMS_CHOICES, default='NET30')
    credit_limit = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    currency = models.CharField(max_length=10, default='INR')
    
    # Performance Ratings
    quality_rating = models.DecimalField(
        max_digits=3, decimal_places=1, default=0,
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    delivery_rating = models.DecimalField(
        max_digits=3, decimal_places=1, default=0,
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    price_competitiveness = models.BooleanField(default=True)
    
    # Certifications
    iso_certified = models.BooleanField(default=False)
    quality_certifications = models.TextField(blank=True, help_text="ISO, BIS, etc.")
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Raw Material Supplier"
        verbose_name_plural = "Raw Material Suppliers"
        ordering = ['name']
    
    def __str__(self):
        return f"{self.supplier_code} - {self.name}"
    
    def get_average_rating(self):
        """Calculate average rating from quality and delivery"""
        return round((self.quality_rating + self.delivery_rating) / 2, 2)


# ============================================================================
# 3. RAW MATERIAL MASTER
# ============================================================================

class RawMaterial(models.Model):
    """Master data for raw materials"""
    
    UNIT_CHOICES = [
        ('KG', 'Kilogram'),
        ('MT', 'Metric Ton'),
        ('LTR', 'Litre'),
        ('PCS', 'Pieces'),
        ('BOX', 'Box'),
        ('ROLL', 'Roll'),
    ]
    
    # Basic Information
    product_code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.ForeignKey(RawMaterialCategory, on_delete=models.PROTECT)
    unit_of_measure = models.CharField(max_length=20, choices=UNIT_CHOICES)
    
    # Specifications
    hsn_code = models.CharField(max_length=20, blank=True, help_text="HSN code for GST")
    density = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_recyclable = models.BooleanField(default=True)
    biodegradability_days = models.IntegerField(null=True, blank=True, help_text="Days to biodegrade")
    
    # Default Supplier & Pricing
    default_supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True)
    current_unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    last_price_update = models.DateTimeField(auto_now=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_hazardous = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Raw Material"
        verbose_name_plural = "Raw Materials"
        ordering = ['category', 'name']
    
    def __str__(self):
        return f"{self.product_code} - {self.name}"
    
    def get_current_stock(self):
        """Get current stock from latest Stock record"""
        try:
            stock = self.stock.latest('updated_at')
            return stock.quantity_on_hand
        except Stock.DoesNotExist:
            return Decimal('0.00')
    
    def get_available_stock(self):
        """Calculate available stock (on hand - reserved)"""
        try:
            stock = self.stock.latest('updated_at')
            return stock.get_available_quantity()
        except Stock.DoesNotExist:
            return Decimal('0.00')
    
    def is_low_stock(self):
        """Check if stock is below minimum"""
        try:
            stock = self.stock.latest('updated_at')
            return stock.quantity_on_hand < stock.minimum_stock_level
        except Stock.DoesNotExist:
            return False


# ============================================================================
# 4. STOCK MANAGEMENT
# ============================================================================

class Stock(models.Model):
    """Current stock levels for raw materials"""
    
    VALUATION_METHODS = [
        ('FIFO', 'First In First Out'),
        ('LIFO', 'Last In First Out'),
        ('WEIGHTED', 'Weighted Average Cost'),
        ('STANDARD', 'Standard Cost'),
    ]
    
    raw_material = models.OneToOneField(RawMaterial, on_delete=models.CASCADE, related_name='stock')
    
    # Stock Quantities
    quantity_on_hand = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    quantity_reserved = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    quantity_damaged = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Thresholds & Triggers
    minimum_stock_level = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    maximum_stock_level = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    reorder_quantity = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    lead_time_days = models.IntegerField(default=7, help_text="Days to receive after ordering")
    
    # Valuation
    valuation_method = models.CharField(max_length=20, choices=VALUATION_METHODS, default='FIFO')
    standard_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    actual_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Warehouse
    warehouse_location = models.CharField(max_length=100, blank=True, help_text="Bin/Rack location")
    
    # timestamps
    last_stock_check = models.DateField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Raw Material Stock"
        verbose_name_plural = "Raw Material Stocks"
    
    def __str__(self):
        return f"Stock: {self.raw_material.name}"
    
    def get_available_quantity(self):
        """Calculate available quantity"""
        return self.quantity_on_hand - self.quantity_reserved - self.quantity_damaged
    
    def get_stock_value(self):
        """Calculate total stock value"""
        return self.quantity_on_hand * self.standard_cost
    
    def needs_reorder(self):
        """Check if reorder is needed"""
        return self.quantity_on_hand < self.minimum_stock_level
    
    def days_until_stockout(self):
        """Estimate days until stock runs out based on average consumption"""
        # This would require consumption tracking
        pass


# ============================================================================
# 5. STOCK MOVEMENTS (Audit Trail)
# ============================================================================

class StockMovement(models.Model):
    """Track all stock movements for audit trail"""
    
    MOVEMENT_TYPE_CHOICES = [
        ('IN_PURCHASE', 'Purchase Order Receipt'),
        ('IN_RETURN', 'Purchase Return'),
        ('OUT_PRODUCTION', 'Production Consumption'),
        ('OUT_SCRAP', 'Scrap/Waste'),
        ('ADJUSTMENT', 'Stock Adjustment'),
        ('TRANSFER', 'Internal Transfer'),
        ('DAMAGE', 'Damage/Loss'),
    ]
    
    raw_material = models.ForeignKey(RawMaterial, on_delete=models.CASCADE, related_name='movements')
    movement_type = models.CharField(max_length=50, choices=MOVEMENT_TYPE_CHOICES)
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_value = models.DecimalField(max_digits=15, decimal_places=2, default=0, editable=False)
    
    # Reference
    purchase_order = models.ForeignKey('PurchaseOrder', on_delete=models.SET_NULL, null=True, blank=True)
    production_order = models.CharField(max_length=50, blank=True)
    reference_number = models.CharField(max_length=100, blank=True)
    
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        verbose_name = "Stock Movement"
        verbose_name_plural = "Stock Movements"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_movement_type_display()} - {self.raw_material.name}"
    
    def save(self, *args, **kwargs):
        self.total_value = self.quantity * self.unit_price
        super().save(*args, **kwargs)


# ============================================================================
# 6. PURCHASE ORDERS FOR RAW MATERIALS
# ============================================================================

class PurchaseOrder(models.Model):
    """Purchase orders for raw materials"""
    
    PO_STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('APPROVED', 'Approved'),
        ('ORDERED', 'Ordered with Supplier'),
        ('PARTIALLY_RECEIVED', 'Partially Received'),
        ('RECEIVED', 'Fully Received'),
        ('INVOICED', 'Invoiced'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    po_number = models.CharField(max_length=50, unique=True)
    po_date = models.DateField(auto_now_add=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name='purchase_orders')
    
    # Line Items (Can have multiple materials)
    raw_material = models.ForeignKey(RawMaterial, on_delete=models.PROTECT)
    quantity_ordered = models.DecimalField(max_digits=12, decimal_places=2)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    line_total = models.DecimalField(max_digits=15, decimal_places=2, editable=False)
    
    # Delivery
    expected_delivery_date = models.DateField()
    actual_delivery_date = models.DateField(null=True, blank=True)
    warehouse_location = models.CharField(max_length=100, blank=True)
    
    # Status & Approval
    status = models.CharField(max_length=20, choices=PO_STATUS_CHOICES, default='DRAFT')
    approval_date = models.DateField(null=True, blank=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_pos')
    
    # Quantity Tracking
    quantity_received = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    quantity_rejected = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_pos')
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Raw Material Purchase Order"
        verbose_name_plural = "Raw Material Purchase Orders"
        ordering = ['-po_date']
    
    def __str__(self):
        return f"PO-{self.po_number}"
    
    def save(self, *args, **kwargs):
        self.line_total = self.quantity_ordered * self.unit_price
        super().save(*args, **kwargs)
    
    def approve(self, user):
        """Approve the purchase order"""
        self.status = 'APPROVED'
        self.approved_by = user
        self.approval_date = timezone.now().date()
        self.save()
    
    def mark_ordered(self):
        """Mark as ordered with supplier"""
        self.status = 'ORDERED'
        self.save()
    
    def is_overdue(self):
        """Check if delivery is overdue"""
        if self.status not in ['RECEIVED', 'CANCELLED']:
            return timezone.now().date() > self.expected_delivery_date
        return False


# ============================================================================
# 7. GOODS RECEIPT NOTE (GRN)
# ============================================================================

class GoodsReceiptNote(models.Model):
    """Record receipt of purchased raw materials"""
    
    grn_number = models.CharField(max_length=50, unique=True)
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.PROTECT, related_name='grns')
    
    receipt_date = models.DateTimeField(auto_now_add=True)
    quantity_received = models.DecimalField(max_digits=12, decimal_places=2)
    quantity_accepted = models.DecimalField(max_digits=12, decimal_places=2)
    quantity_rejected = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Quality Check
    quality_check_passed = models.BooleanField(default=True)
    quality_notes = models.TextField(blank=True)
    
    # Warehouse
    received_in_location = models.CharField(max_length=100)
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Goods Receipt Note"
        verbose_name_plural = "Goods Receipt Notes"
        ordering = ['-receipt_date']
    
    def __str__(self):
        return f"GRN-{self.grn_number}"
    
    def save(self, *args, **kwargs):
        """Auto-generate GRN number if not provided"""
        if not self.grn_number:
            last_grn = GoodsReceiptNote.objects.order_by('-id').first()
            next_id = (last_grn.id + 1) if last_grn else 1
            self.grn_number = f"GRN-{timezone.now().strftime('%Y%m%d')}-{next_id}"
        super().save(*args, **kwargs)


# ============================================================================
# 8. AUTO-REORDER SETTINGS
# ============================================================================

class AutoReorderSetting(models.Model):
    """Configuration for automatic purchase order generation"""
    
    raw_material = models.OneToOneField(RawMaterial, on_delete=models.CASCADE, related_name='auto_reorder')
    
    is_enabled = models.BooleanField(default=False)
    trigger_stock_level = models.DecimalField(max_digits=12, decimal_places=2)
    auto_reorder_quantity = models.DecimalField(max_digits=12, decimal_places=2)
    
    preferred_supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True)
    
    notify_days_before = models.IntegerField(default=5, help_text="Days before stock runs out")
    auto_generate_po = models.BooleanField(default=False, help_text="Auto-create PO without approval")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Auto Reorder Setting"
        verbose_name_plural = "Auto Reorder Settings"
    
    def __str__(self):
        return f"Auto-Reorder: {self.raw_material.name}"


# ============================================================================
# 9. STOCK ALERTS
# ============================================================================

class StockAlert(models.Model):
    """Alerts for stock management"""
    
    ALERT_TYPE_CHOICES = [
        ('LOW_STOCK', 'Low Stock Warning'),
        ('OUT_OF_STOCK', 'Out of Stock'),
        ('QUALITY_ISSUE', 'Quality Issue'),
        ('STOCK_DAMAGE', 'Stock Damaged'),
        ('SLOW_MOVING', 'Slow Moving Stock'),
        ('EXPIRY_SOON', 'Expiry Coming Soon'),
    ]
    
    SEVERITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    ]
    
    raw_material = models.ForeignKey(RawMaterial, on_delete=models.CASCADE, related_name='alerts')
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPE_CHOICES)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='MEDIUM')
    
    message = models.TextField()
    
    is_active = models.BooleanField(default=True)
    is_acknowledged = models.BooleanField(default=False)
    acknowledged_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    
    action_taken = models.TextField(blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Stock Alert"
        verbose_name_plural = "Stock Alerts"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_alert_type_display()} - {self.raw_material.name}"
    
    def acknowledge(self, user):
        """Mark alert as acknowledged"""
        self.is_acknowledged = True
        self.acknowledged_by = user
        self.acknowledged_at = timezone.now()
        self.save()
    
    def resolve(self, action_text=''):
        """Mark alert as resolved"""
        self.is_active = False
        self.action_taken = action_text
        self.resolved_at = timezone.now()
        self.save()


# ============================================================================
# 10. MATERIAL CONSUMPTION TRACKING
# ============================================================================

class MaterialConsumption(models.Model):
    """Track material consumption in production"""
    
    raw_material = models.ForeignKey(RawMaterial, on_delete=models.PROTECT, related_name='consumption')
    production_order = models.CharField(max_length=50)  # Link to Manufacturing module
    
    planned_quantity = models.DecimalField(max_digits=12, decimal_places=2)
    actual_quantity = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    cost_per_unit = models.DecimalField(max_digits=12, decimal_places=2)
    total_cost = models.DecimalField(max_digits=15, decimal_places=2, editable=False)
    
    consumption_date = models.DateTimeField(auto_now_add=True)
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        verbose_name = "Material Consumption"
        verbose_name_plural = "Material Consumption"
    
    def __str__(self):
        return f"{self.raw_material.name} - PO: {self.production_order}"
    
    def save(self, *args, **kwargs):
        self.total_cost = (self.actual_quantity or self.planned_quantity) * self.cost_per_unit
        super().save(*args, **kwargs)
