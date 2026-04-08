from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class RawMaterialCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Raw Material Category"
        verbose_name_plural = "Raw Material Categories"
    
    def __str__(self):
        return self.name

class Supplier(models.Model):
    PAYMENT_TERMS = [("CASH","Cash"),("NET30","NET 30"),("NET60","NET 60")]
    supplier_code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    contact_person = models.CharField(max_length=255, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    payment_terms = models.CharField(max_length=20, choices=PAYMENT_TERMS, default="NET30")
    credit_limit = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    currency = models.CharField(max_length=10, default="INR")
    quality_rating = models.DecimalField(max_digits=3, decimal_places=1, default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} ({self.supplier_code})"

class RawMaterial(models.Model):
    UNIT_CHOICES = [("KG","Kg"),("MT","MT"),("LTR","Litre"),("PCS","Pieces")]
    product_code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.ForeignKey(RawMaterialCategory, on_delete=models.PROTECT)
    unit_of_measure = models.CharField(max_length=20, choices=UNIT_CHOICES)
    hsn_code = models.CharField(max_length=20, blank=True)
    default_supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True)
    current_unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Raw Material"
        verbose_name_plural = "Raw Materials"
    
    def __str__(self):
        return f"{self.product_code} - {self.name}"

class Stock(models.Model):
    VALUATION = [("FIFO","FIFO"),("LIFO","LIFO"),("WEIGHTED","Weighted"),("STANDARD","Standard")]
    raw_material = models.OneToOneField(RawMaterial, on_delete=models.CASCADE, related_name="stock")
    quantity_on_hand = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    quantity_reserved = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    quantity_damaged = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    minimum_stock_level = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    maximum_stock_level = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    reorder_quantity = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    lead_time_days = models.IntegerField(default=7)
    valuation_method = models.CharField(max_length=20, choices=VALUATION, default="FIFO")
    standard_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    warehouse_location = models.CharField(max_length=100, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Stock - {self.raw_material}"

class StockMovement(models.Model):
    TYPES = [("IN_PURCHASE","Receipt"),("OUT_PRODUCTION","Production"),("ADJUSTMENT","Adjustment")]
    raw_material = models.ForeignKey(RawMaterial, on_delete=models.CASCADE, related_name="movements")
    movement_type = models.CharField(max_length=50, choices=TYPES)
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_value = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    production_order = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    def __str__(self):
        return f"{self.movement_type} - {self.raw_material}"

class PurchaseOrder(models.Model):
    STATUS = [("DRAFT","Draft"),("APPROVED","Approved"),("ORDERED","Ordered"),("RECEIVED","Received")]
    po_number = models.CharField(max_length=50, unique=True)
    po_date = models.DateField(auto_now_add=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT)
    raw_material = models.ForeignKey(RawMaterial, on_delete=models.PROTECT)
    quantity_ordered = models.DecimalField(max_digits=12, decimal_places=2)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    expected_delivery_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS, default="DRAFT")
    quantity_received = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.po_number
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

class GoodsReceiptNote(models.Model):
    grn_number = models.CharField(max_length=50, unique=True)
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.PROTECT)
    receipt_date = models.DateTimeField(auto_now_add=True)
    quantity_received = models.DecimalField(max_digits=12, decimal_places=2)
    quantity_accepted = models.DecimalField(max_digits=12, decimal_places=2)
    quantity_rejected = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    quality_notes = models.TextField(blank=True)
    received_in_location = models.CharField(max_length=100)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    def __str__(self):
        return self.grn_number

class AutoReorderSetting(models.Model):
    raw_material = models.OneToOneField(RawMaterial, on_delete=models.CASCADE, related_name="auto_reorder")
    is_enabled = models.BooleanField(default=False)
    trigger_stock_level = models.DecimalField(max_digits=12, decimal_places=2)
    auto_reorder_quantity = models.DecimalField(max_digits=12, decimal_places=2)
    preferred_supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True)
    notify_days_before = models.IntegerField(default=5)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Auto Reorder - {self.raw_material}"

class StockAlert(models.Model):
    TYPES = [("LOW_STOCK","Low Stock"),("OUT_OF_STOCK","Out"),("QUALITY","Quality")]
    SEVERITY = [("MEDIUM","Medium"),("HIGH","High"),("CRITICAL","Critical")]
    raw_material = models.ForeignKey(RawMaterial, on_delete=models.CASCADE, related_name="alerts")
    alert_type = models.CharField(max_length=20, choices=TYPES)
    severity = models.CharField(max_length=20, choices=SEVERITY, default="MEDIUM")
    message = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.alert_type} - {self.raw_material}"

class MaterialConsumption(models.Model):
    raw_material = models.ForeignKey(RawMaterial, on_delete=models.PROTECT)
    production_order = models.CharField(max_length=50)
    planned_quantity = models.DecimalField(max_digits=12, decimal_places=2)
    actual_quantity = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    cost_per_unit = models.DecimalField(max_digits=12, decimal_places=2)
    consumption_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Consumption - {self.raw_material} - {self.production_order}"
