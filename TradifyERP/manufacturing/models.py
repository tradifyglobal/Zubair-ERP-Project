"""
Manufacturing Module Models
Complete manufacturing operations including:
- Bill of Materials (BOM)
- Production Planning & Control (MRP)
- Work Orders & Shop Floor Control
- Quality Control & Inspection
- Equipment & Maintenance
- Inventory (Raw Materials, WIP, Finished Goods)

Fully integrated with accounting for cost tracking and GL posting.
Implements industry best practices (ISO 9001, APICS CPIM standards).
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal
import uuid


class ProductCategory(models.Model):
    """Product categories and classifications."""
    entity = models.ForeignKey(
        'accounting.Entity',
        on_delete=models.CASCADE,
        related_name='product_categories'
    )
    
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20)
    description = models.TextField(blank=True)
    
    # GL Integration
    revenue_account = models.ForeignKey(
        'accounting.Account',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='product_categories_revenue',
        help_text="Revenue account for this product category"
    )
    
    cogs_account = models.ForeignKey(
        'accounting.Account',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='product_categories_cogs',
        help_text="COGS account for this product category"
    )
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        unique_together = ('entity', 'code')
    
    def __str__(self):
        return f"{self.name} ({self.code})"


class Product(models.Model):
    """
    Finished goods and saleable products.
    Links to BOM for manufacturing.
    """
    entity = models.ForeignKey(
        'accounting.Entity',
        on_delete=models.CASCADE,
        related_name='products'
    )
    
    # Identification
    product_code = models.CharField(max_length=50, unique=True, db_index=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Classification
    category = models.ForeignKey(
        ProductCategory,
        on_delete=models.SET_NULL,
        null=True,
        related_name='products'
    )
    
    # Manufacturing Details
    is_manufactured = models.BooleanField(default=True, help_text="Made in-house vs purchased")
    manufacturing_lead_time = models.IntegerField(default=7, help_text="Days to manufacture")
    standard_batch_size = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=1,
        validators=[MinValueValidator(0.01)]
    )
    
    # Specifications
    unit_of_measure = models.CharField(max_length=10, default='UNIT')
    weight = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    dimensions = models.CharField(max_length=100, blank=True, help_text="L x W x H")
    
    # Costing
    standard_cost = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    selling_price = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    
    # GL Integration
    inventory_account = models.ForeignKey(
        'accounting.Account',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products_inventory',
        help_text="Finished goods inventory account"
    )
    
    # Quality & Compliance
    requires_inspection = models.BooleanField(default=True)
    inspection_level = models.CharField(
        max_length=20,
        choices=[
            ('NONE', 'No Inspection'),
            ('BASIC', 'Basic Inspection'),
            ('FULL', 'Full Inspection'),
            ('CERTIFIED', 'Certified Testing'),
        ],
        default='BASIC'
    )
    
    # Status
    is_active = models.BooleanField(default=True)
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_products'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['product_code']
        indexes = [
            models.Index(fields=['product_code']),
            models.Index(fields=['entity', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.product_code})"


class RawMaterial(models.Model):
    """
    Raw materials and components for manufacturing.
    Tracked in inventory and linked to products via BOM.
    """
    entity = models.ForeignKey(
        'accounting.Entity',
        on_delete=models.CASCADE,
        related_name='raw_materials'
    )
    
    # Identification
    material_code = models.CharField(max_length=50, unique=True, db_index=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    supplier = models.CharField(max_length=100, blank=True)
    
    # Specifications
    unit_of_measure = models.CharField(max_length=10, default='UNIT')
    reorder_quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=100,
        validators=[MinValueValidator(0)]
    )
    reorder_point = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=50,
        validators=[MinValueValidator(0)]
    )
    
    # Costing
    standard_unit_cost = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    
    # GL Integration
    inventory_account = models.ForeignKey(
        'accounting.Account',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='raw_materials_inventory',
        help_text="Raw materials inventory account"
    )
    
    # Tracking
    current_stock = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['material_code']
        indexes = [
            models.Index(fields=['material_code']),
            models.Index(fields=['entity', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.material_code})"


class BillOfMaterials(models.Model):
    """
    Bill of Materials (BOM) - recipe for manufacturing products.
    Defines components and quantities needed for production.
    """
    entity = models.ForeignKey(
        'accounting.Entity',
        on_delete=models.CASCADE,
        related_name='bills_of_materials'
    )
    
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='boms'
    )
    
    # BOM Code
    bom_code = models.CharField(max_length=100, unique=True, db_index=True, null=True, blank=True)
    
    # Versioning
    version = models.IntegerField(default=1)
    effective_date = models.DateField(default=timezone.now)
    end_date = models.DateField(null=True, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Approval
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_boms'
    )
    approved_date = models.DateTimeField(null=True, blank=True)
    
    # Notes
    notes = models.TextField(blank=True)
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_boms'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-effective_date', '-version']
        unique_together = ('product', 'version')
    
    def __str__(self):
        return f"BOM {self.product.product_code} v{self.version}"
    
    def get_total_material_cost(self):
        """Calculate total material cost for one unit."""
        return sum(line.total_cost for line in self.lines.all())


class BOMLine(models.Model):
    """Line items in a Bill of Materials."""
    bom = models.ForeignKey(
        BillOfMaterials,
        on_delete=models.CASCADE,
        related_name='lines'
    )
    
    material = models.ForeignKey(
        RawMaterial,
        on_delete=models.PROTECT,
        related_name='bom_lines'
    )
    
    # Quantity
    quantity_per_unit = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        validators=[MinValueValidator(0.001)],
        help_text="Quantity of material per product unit"
    )
    
    # Waste & Scrap allowance
    scrap_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    
    # Costing
    unit_cost = models.DecimalField(max_digits=18, decimal_places=2)
    
    @property
    def total_cost(self):
        """Total cost for this line (with scrap allowance)."""
        base_cost = self.quantity_per_unit * self.unit_cost
        scrap_cost = base_cost * (self.scrap_percentage / 100)
        return base_cost + scrap_cost
    
    # Line status
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['bom', 'material']
    
    def __str__(self):
        return f"{self.bom} - {self.material.name}"


class WorkCenter(models.Model):
    """
    Production work centers / machines / departments.
    Used for capacity planning and scheduling.
    """
    entity = models.ForeignKey(
        'accounting.Entity',
        on_delete=models.CASCADE,
        related_name='work_centers'
    )
    
    # Identification
    code = models.CharField(max_length=20)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    # Capacity
    standard_hours_per_day = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=8
    )
    
    # Cost
    labor_cost_per_hour = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    machine_cost_per_hour = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    
    # GL Integration
    labor_expense_account = models.ForeignKey(
        'accounting.Account',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='work_centers_labor',
        help_text="Labor cost account"
    )
    
    machine_expense_account = models.ForeignKey(
        'accounting.Account',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='work_centers_machine',
        help_text="Machine/overhead cost account"
    )
    
    # Status
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['code']
        unique_together = ('entity', 'code')
    
    def __str__(self):
        return f"{self.name} ({self.code})"
    
    @property
    def total_hourly_cost(self):
        """Total cost per hour (labor + machine)."""
        return self.labor_cost_per_hour + self.machine_cost_per_hour


class Routing(models.Model):
    """
    Routing - sequence of work centers for manufacturing a product.
    Defines which machines/departments and sequence.
    """
    entity = models.ForeignKey(
        'accounting.Entity',
        on_delete=models.CASCADE,
        related_name='routings'
    )
    
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='routings'
    )
    
    # Versioning
    version = models.IntegerField(default=1)
    effective_date = models.DateField(default=timezone.now)
    end_date = models.DateField(null=True, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Approval
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_routings'
    )
    approved_date = models.DateTimeField(null=True, blank=True)
    
    notes = models.TextField(blank=True)
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_routings'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-effective_date', '-version']
        unique_together = ('product', 'version')
    
    def __str__(self):
        return f"Routing {self.product.product_code} v{self.version}"
    
    def get_total_labor_hours(self):
        """Calculate total labor hours needed."""
        return sum(line.estimated_hours for line in self.lines.all())


class RoutingLine(models.Model):
    """Line items in a routing - work center sequence."""
    routing = models.ForeignKey(
        Routing,
        on_delete=models.CASCADE,
        related_name='lines'
    )
    
    work_center = models.ForeignKey(
        WorkCenter,
        on_delete=models.PROTECT,
        related_name='routing_lines'
    )
    
    # Sequence
    sequence = models.IntegerField(help_text="Operation sequence number")
    
    # Time
    estimated_hours = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    
    # Setup time
    setup_hours = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    
    # Process parameters
    machine_parameters = models.TextField(blank=True, help_text="Speed, temperature, etc.")
    
    # Status
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['routing', 'sequence']
        unique_together = ('routing', 'sequence')
    
    def __str__(self):
        return f"{self.routing} - Step {self.sequence}: {self.work_center.name}"
    
    @property
    def total_hours(self):
        """Total hours including setup."""
        return self.estimated_hours + self.setup_hours


class ProductionOrder(models.Model):
    """
    Production Orders (Work Orders) - instructions to manufacture products.
    Linked to sales orders and MRP planning.
    """
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('PLANNED', 'Planned'),
        ('RELEASED', 'Released to Shop Floor'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETE', 'Complete'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    entity = models.ForeignKey(
        'accounting.Entity',
        on_delete=models.CASCADE,
        related_name='production_orders'
    )
    
    # Identification
    po_number = models.CharField(max_length=50, unique=True, db_index=True)
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='production_orders'
    )
    
    # Quantities
    quantity_ordered = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    quantity_completed = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    quantity_scrapped = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    
    # Dates
    start_date = models.DateField()
    due_date = models.DateField()
    completion_date = models.DateField(null=True, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    
    # Costing
    estimated_material_cost = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0
    )
    estimated_labor_cost = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0
    )
    actual_material_cost = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0
    )
    actual_labor_cost = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0
    )
    
    # References
    sales_order_number = models.CharField(max_length=50, blank=True)
    bom = models.ForeignKey(
        BillOfMaterials,
        on_delete=models.SET_NULL,
        null=True,
        related_name='production_orders'
    )
    routing = models.ForeignKey(
        Routing,
        on_delete=models.SET_NULL,
        null=True,
        related_name='production_orders'
    )
    
    # Approval
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_production_orders'
    )
    approved_date = models.DateTimeField(null=True, blank=True)
    
    # Audit
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_production_orders'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-due_date']
        indexes = [
            models.Index(fields=['po_number']),
            models.Index(fields=['status', 'due_date']),
            models.Index(fields=['entity', 'status']),
        ]
    
    def __str__(self):
        return f"PO {self.po_number} - {self.product.name}"
    
    @property
    def total_estimated_cost(self):
        return self.estimated_material_cost + self.estimated_labor_cost
    
    @property
    def total_actual_cost(self):
        return self.actual_material_cost + self.actual_labor_cost


class QualityInspection(models.Model):
    """
    Quality Control and Inspection records.
    Tracks inspection results and defects.
    """
    INSPECTION_STATUS = [
        ('PASS', 'Passed'),
        ('FAIL', 'Failed'),
        ('REWORK', 'Rework Required'),
    ]
    
    entity = models.ForeignKey(
        'accounting.Entity',
        on_delete=models.CASCADE,
        related_name='quality_inspections'
    )
    
    production_order = models.ForeignKey(
        ProductionOrder,
        on_delete=models.CASCADE,
        related_name='inspections'
    )
    
    # Inspection Number
    inspection_number = models.CharField(max_length=100, unique=True, db_index=True, null=True, blank=True)
    
    # Inspection Details
    inspection_date = models.DateTimeField(default=timezone.now)
    quantity_inspected = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    
    # Results
    status = models.CharField(max_length=20, choices=INSPECTION_STATUS)
    defects_found = models.TextField(blank=True)
    defect_count = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    
    # Notes
    notes = models.TextField(blank=True)
    
    # Inspector
    inspected_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='quality_inspections'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-inspection_date']
    
    def __str__(self):
        return f"Inspection {self.production_order.po_number} - {self.status}"


class Equipment(models.Model):
    """
    Manufacturing equipment / machines.
    Tracks maintenance and utilization.
    """
    STATUS_CHOICES = [
        ('OPERATIONAL', 'Operational'),
        ('MAINTENANCE', 'Under Maintenance'),
        ('REPAIR', 'Being Repaired'),
        ('RETIRED', 'Retired'),
    ]
    
    entity = models.ForeignKey(
        'accounting.Entity',
        on_delete=models.CASCADE,
        related_name='manufacturing_equipment'
    )
    
    # Identification
    equipment_code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    model = models.CharField(max_length=100, blank=True)
    serial_number = models.CharField(max_length=100, blank=True)
    
    # Details
    description = models.TextField(blank=True)
    acquisition_date = models.DateField()
    acquisition_cost = models.DecimalField(max_digits=18, decimal_places=2)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='OPERATIONAL')
    
    # Maintenance
    last_maintenance_date = models.DateField(null=True, blank=True)
    next_maintenance_date = models.DateField(null=True, blank=True)
    maintenance_interval_days = models.IntegerField(default=90)
    
    # GL Integration
    fixed_asset_account = models.ForeignKey(
        'accounting.Account',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='manufacturing_equipment',
        help_text="Fixed asset account"
    )
    
    depreciation_account = models.ForeignKey(
        'accounting.Account',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='manufacturing_equipment_depreciation',
        help_text="Accumulated depreciation account"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['equipment_code']
        indexes = [
            models.Index(fields=['equipment_code']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.equipment_code})"
