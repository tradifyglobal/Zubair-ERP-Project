from django.db import models
from django.utils import timezone
from sales.models import Customer


class Category(models.Model):
    """Product Category"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'inventory_category'
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class Product(models.Model):
    """Product/SKU information"""
    SKU_STATUS_CHOICES = [
        ('active', 'Active'),
        ('discontinued', 'Discontinued'),
        ('obsolete', 'Obsolete'),
    ]

    sku = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
    
    # Pricing
    cost_price = models.DecimalField(max_digits=12, decimal_places=2, help_text="Cost to purchase")
    selling_price = models.DecimalField(max_digits=12, decimal_places=2, help_text="Standard selling price")
    
    # Inventory tracking
    reorder_level = models.IntegerField(default=10, help_text="Minimum stock level for reordering")
    reorder_quantity = models.IntegerField(default=50, help_text="Quantity to order when restocking")
    
    status = models.CharField(max_length=20, choices=SKU_STATUS_CHOICES, default='active')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'inventory_product'
        ordering = ['sku']
        indexes = [
            models.Index(fields=['sku']),
            models.Index(fields=['status']),
            models.Index(fields=['category']),
        ]

    def __str__(self):
        return f"{self.sku} - {self.name}"

    @property
    def profit_margin(self):
        """Calculate profit margin percentage"""
        if self.cost_price == 0:
            return 0
        return ((self.selling_price - self.cost_price) / self.cost_price) * 100


class Warehouse(models.Model):
    """Physical warehouse/storage location"""
    name = models.CharField(max_length=100, unique=True)
    location = models.CharField(max_length=255)
    contact_person = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'inventory_warehouse'
        ordering = ['name']

    def __str__(self):
        return self.name


class Stock(models.Model):
    """Current stock levels by product and warehouse"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stocks')
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='stocks')
    
    quantity_on_hand = models.IntegerField(default=0)
    quantity_reserved = models.IntegerField(default=0, help_text="Reserved for pending orders")
    quantity_available = models.IntegerField(default=0, help_text="Available for sale")
    
    last_counted_at = models.DateTimeField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'inventory_stock'
        unique_together = ('product', 'warehouse')
        indexes = [
            models.Index(fields=['product', 'warehouse']),
            models.Index(fields=['quantity_available']),
        ]

    def __str__(self):
        return f"{self.product.sku} @ {self.warehouse.name}: {self.quantity_on_hand}"

    def save(self, *args, **kwargs):
        """Auto-calculate available quantity"""
        self.quantity_available = self.quantity_on_hand - self.quantity_reserved
        super().save(*args, **kwargs)


class StockMovement(models.Model):
    """Log all stock movements for audit trail"""
    MOVEMENT_TYPE_CHOICES = [
        ('in', 'Stock In'),
        ('out', 'Stock Out'),
        ('adjustment', 'Adjustment'),
        ('transfer', 'Transfer'),
        ('return', 'Return'),
        ('damage', 'Damage/Loss'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='movements')
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='movements')
    
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPE_CHOICES)
    quantity = models.IntegerField()
    reference_number = models.CharField(max_length=100, blank=True, help_text="PO, Invoice, or Transfer number")
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(max_length=100, blank=True)

    class Meta:
        db_table = 'inventory_stock_movement'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['product', 'warehouse']),
            models.Index(fields=['created_at']),
            models.Index(fields=['movement_type']),
        ]

    def __str__(self):
        return f"{self.get_movement_type_display()}: {self.product.sku} - {self.quantity}"


class PurchaseOrder(models.Model):
    """Purchase Order for restocking"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('received', 'Received'),
        ('cancelled', 'Cancelled'),
    ]

    po_number = models.CharField(max_length=50, unique=True)
    supplier = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    warehouse = models.ForeignKey(Warehouse, on_delete=models.SET_NULL, null=True)
    
    expected_delivery_date = models.DateField(blank=True, null=True)
    actual_delivery_date = models.DateField(blank=True, null=True)
    
    total_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'inventory_purchase_order'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['po_number']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"PO-{self.po_number}"


class PurchaseOrderLine(models.Model):
    """Individual line items in a Purchase Order"""
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='lines')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    
    quantity_ordered = models.IntegerField()
    quantity_received = models.IntegerField(default=0)
    unit_cost = models.DecimalField(max_digits=12, decimal_places=2)
    
    line_total = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'inventory_purchase_order_line'

    def __str__(self):
        return f"{self.purchase_order.po_number} - {self.product.sku}"

    def save(self, *args, **kwargs):
        """Auto-calculate line total"""
        self.line_total = self.quantity_ordered * self.unit_cost
        super().save(*args, **kwargs)


class InventoryAdjustment(models.Model):
    """Record inventory adjustments (physical counts, corrections)"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    adjustment_number = models.CharField(max_length=50, unique=True)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    reason = models.CharField(max_length=255)
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'inventory_adjustment'
        ordering = ['-created_at']

    def __str__(self):
        return f"ADJ-{self.adjustment_number}"


class InventoryAdjustmentLine(models.Model):
    """Line items for inventory adjustments"""
    adjustment = models.ForeignKey(InventoryAdjustment, on_delete=models.CASCADE, related_name='lines')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    
    quantity_on_hand = models.IntegerField(help_text="Current system quantity")
    quantity_counted = models.IntegerField(help_text="Physically counted quantity")
    quantity_difference = models.IntegerField(help_text="Difference (counted - on_hand)")
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'inventory_adjustment_line'

    def __str__(self):
        return f"{self.adjustment.adjustment_number} - {self.product.sku}"

    def save(self, *args, **kwargs):
        """Auto-calculate difference"""
        self.quantity_difference = self.quantity_counted - self.quantity_on_hand
        super().save(*args, **kwargs)
