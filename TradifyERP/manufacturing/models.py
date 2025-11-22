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


# ============================================================================
# DISTRIBUTOR MANAGEMENT & AFTER-SALES SERVICE
# ============================================================================


class Distributor(models.Model):
    """Distributor master record."""
    
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'),
        ('SUSPENDED', 'Suspended'),
        ('PROSPECTIVE', 'Prospective'),
    ]
    
    entity = models.ForeignKey(
        'accounting.Entity',
        on_delete=models.CASCADE,
        related_name='distributors'
    )
    
    # Distributor Info
    distributor_code = models.CharField(max_length=50, unique=True, db_index=True)
    distributor_name = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PROSPECTIVE')
    
    # Contact Details
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    website = models.URLField(blank=True)
    
    # Address
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    
    # Account Manager
    account_manager = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='managed_distributors'
    )
    
    # Territory/Region
    region = models.CharField(max_length=100, blank=True)
    territory = models.CharField(max_length=100, blank=True)
    
    # Relationship Details
    date_onboarded = models.DateField(default=timezone.now)
    contract_start_date = models.DateField(null=True, blank=True)
    contract_end_date = models.DateField(null=True, blank=True)
    
    # Performance
    credit_limit = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    annual_sales_target = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    ytd_sales = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    
    # Products Authorized
    authorized_products = models.TextField(blank=True, help_text="Comma-separated product codes")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'manufacturing_distributor'
        ordering = ['distributor_name']
        indexes = [
            models.Index(fields=['entity', 'status']),
            models.Index(fields=['distributor_code']),
            models.Index(fields=['region']),
        ]
    
    def __str__(self):
        return f"{self.distributor_name} ({self.distributor_code})"


class DistributorContact(models.Model):
    """Key contacts at distributor organizations."""
    
    distributor = models.ForeignKey(
        Distributor,
        on_delete=models.CASCADE,
        related_name='contacts'
    )
    
    # Contact Details
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    job_title = models.CharField(max_length=100)
    department = models.CharField(max_length=100, blank=True)
    
    # Communication
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    mobile = models.CharField(max_length=20, blank=True)
    
    # Relationship
    is_primary_contact = models.BooleanField(default=False)
    preferred_contact_method = models.CharField(
        max_length=20,
        choices=[
            ('EMAIL', 'Email'),
            ('PHONE', 'Phone'),
            ('MOBILE', 'Mobile'),
            ('WHATSAPP', 'WhatsApp'),
        ]
    )
    
    # Activity
    last_contact_date = models.DateField(null=True, blank=True)
    next_follow_up = models.DateField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'manufacturing_distributor_contact'
        ordering = ['-is_primary_contact', 'last_name']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.distributor.distributor_name}"


class DistributorOrder(models.Model):
    """Orders placed by distributors."""
    
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('SUBMITTED', 'Submitted'),
        ('CONFIRMED', 'Confirmed'),
        ('SHIPPED', 'Shipped'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    entity = models.ForeignKey(
        'accounting.Entity',
        on_delete=models.CASCADE,
        related_name='distributor_orders'
    )
    
    # Order Identification
    order_number = models.CharField(max_length=50, unique=True, db_index=True)
    distributor = models.ForeignKey(
        Distributor,
        on_delete=models.CASCADE,
        related_name='orders'
    )
    
    # Dates
    order_date = models.DateField(default=timezone.now)
    required_delivery_date = models.DateField()
    actual_delivery_date = models.DateField(null=True, blank=True)
    
    # Order Details
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    description = models.TextField(blank=True)
    
    # Amount
    subtotal = models.DecimalField(max_digits=18, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=18, decimal_places=2)
    
    # Terms
    payment_terms = models.CharField(max_length=50, blank=True)
    
    # Tracking
    is_posted = models.BooleanField(default=False)
    sales_order_reference = models.CharField(max_length=50, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'manufacturing_distributor_order'
        ordering = ['-order_date']
        indexes = [
            models.Index(fields=['entity', 'status']),
            models.Index(fields=['distributor', 'order_date']),
            models.Index(fields=['order_number']),
        ]
    
    def __str__(self):
        return f"Order {self.order_number} - {self.distributor.distributor_name}"


class Courier(models.Model):
    """Courier/Carrier service providers."""
    
    entity = models.ForeignKey(
        'accounting.Entity',
        on_delete=models.CASCADE,
        related_name='couriers'
    )
    
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'manufacturing_courier'
        ordering = ['name']
        unique_together = ('entity', 'code')
    
    def __str__(self):
        return self.name


class OrderShipment(models.Model):
    """Track shipments for distributor orders."""
    
    order = models.ForeignKey(
        DistributorOrder,
        on_delete=models.CASCADE,
        related_name='shipments'
    )
    
    # Shipment Details
    shipment_number = models.CharField(max_length=50, unique=True)
    shipment_date = models.DateField(default=timezone.now)
    expected_delivery = models.DateField()
    actual_delivery = models.DateField(null=True, blank=True)
    
    # Carrier & Tracking
    courier = models.ForeignKey(
        Courier,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='shipments'
    )
    tracking_number = models.CharField(max_length=100, blank=True)
    shipping_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('PENDING', 'Pending'),
            ('IN_TRANSIT', 'In Transit'),
            ('DELIVERED', 'Delivered'),
            ('DELAYED', 'Delayed'),
            ('RETURNED', 'Returned'),
        ]
    )
    
    # Notes
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'manufacturing_order_shipment'
        ordering = ['-shipment_date']
        indexes = [
            models.Index(fields=['order', 'status']),
            models.Index(fields=['tracking_number']),
        ]
    
    def __str__(self):
        return f"Shipment {self.shipment_number}"


class AfterSalesService(models.Model):
    """After-sales service cases and support tickets."""
    
    SERVICE_TYPE = [
        ('WARRANTY_CLAIM', 'Warranty Claim'),
        ('REPAIR', 'Repair'),
        ('MAINTENANCE', 'Maintenance'),
        ('REPLACEMENT', 'Replacement'),
        ('TECHNICAL_SUPPORT', 'Technical Support'),
        ('TRAINING', 'Training'),
    ]
    
    STATUS_CHOICES = [
        ('OPEN', 'Open'),
        ('IN_PROGRESS', 'In Progress'),
        ('WAITING', 'Waiting for Customer'),
        ('RESOLVED', 'Resolved'),
        ('CLOSED', 'Closed'),
    ]
    
    PRIORITY_CHOICES = [
        (1, 'Low'),
        (2, 'Medium'),
        (3, 'High'),
        (4, 'Critical'),
    ]
    
    entity = models.ForeignKey(
        'accounting.Entity',
        on_delete=models.CASCADE,
        related_name='after_sales_services'
    )
    
    # Service Identification
    service_ticket_number = models.CharField(max_length=50, unique=True, db_index=True)
    distributor = models.ForeignKey(
        Distributor,
        on_delete=models.CASCADE,
        related_name='after_sales_services'
    )
    
    # Service Details
    service_type = models.CharField(max_length=30, choices=SERVICE_TYPE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='OPEN')
    priority = models.IntegerField(choices=PRIORITY_CHOICES, default=2)
    
    # Product Reference
    product_code = models.CharField(max_length=100, blank=True)
    serial_number = models.CharField(max_length=100, blank=True)
    purchase_date = models.DateField(null=True, blank=True)
    
    # Issue Details
    issue_description = models.TextField()
    issue_date = models.DateField(default=timezone.now)
    
    # Resolution
    resolution_description = models.TextField(blank=True)
    resolution_date = models.DateField(null=True, blank=True)
    
    # Warranty
    is_under_warranty = models.BooleanField(default=True)
    warranty_expiry_date = models.DateField(null=True, blank=True)
    
    # Cost
    service_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    warranty_covered = models.BooleanField(default=True)
    
    # Tracking
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='assigned_services'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'manufacturing_after_sales_service'
        ordering = ['-issue_date']
        indexes = [
            models.Index(fields=['entity', 'status']),
            models.Index(fields=['distributor']),
            models.Index(fields=['service_ticket_number']),
        ]
    
    def __str__(self):
        return f"Ticket {self.service_ticket_number} - {self.distributor.distributor_name}"


class ServiceActivity(models.Model):
    """Activity log for after-sales service cases."""
    
    ACTIVITY_TYPE = [
        ('COMMENT', 'Comment'),
        ('STATUS_CHANGE', 'Status Change'),
        ('ASSIGNMENT', 'Assignment'),
        ('FOLLOW_UP', 'Follow Up'),
        ('RESOLUTION', 'Resolution'),
        ('ESCALATION', 'Escalation'),
    ]
    
    service = models.ForeignKey(
        AfterSalesService,
        on_delete=models.CASCADE,
        related_name='activities'
    )
    
    # Activity Details
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPE)
    description = models.TextField()
    notes = models.TextField(blank=True)
    
    # Reference
    previous_status = models.CharField(max_length=20, blank=True)
    new_status = models.CharField(max_length=20, blank=True)
    
    # Tracking
    performed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='service_activities'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'manufacturing_service_activity'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.activity_type} on {self.service.service_ticket_number}"


class WarrantyRegistration(models.Model):
    """Product warranty registration and tracking."""
    
    WARRANTY_TYPE = [
        ('STANDARD', 'Standard'),
        ('EXTENDED', 'Extended'),
        ('PREMIUM', 'Premium'),
    ]
    
    # Warranty Details
    warranty_number = models.CharField(max_length=50, unique=True, db_index=True)
    warranty_type = models.CharField(max_length=20, choices=WARRANTY_TYPE, default='STANDARD')
    
    # Product Information
    product_code = models.CharField(max_length=100)
    serial_number = models.CharField(max_length=100)
    
    # Customer/Distributor
    distributor = models.ForeignKey(
        Distributor,
        on_delete=models.CASCADE,
        related_name='warranty_registrations'
    )
    
    end_customer_name = models.CharField(max_length=255, blank=True)
    end_customer_email = models.EmailField(blank=True)
    end_customer_phone = models.CharField(max_length=20, blank=True)
    
    # Warranty Coverage
    purchase_date = models.DateField()
    coverage_start_date = models.DateField(default=timezone.now)
    coverage_end_date = models.DateField()
    
    # Coverage Details
    coverage_description = models.TextField()
    terms_and_conditions = models.TextField(blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_claimed = models.BooleanField(default=False)
    
    # Tracking
    claims_count = models.IntegerField(default=0)
    total_claims_value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'manufacturing_warranty_registration'
        ordering = ['-coverage_start_date']
        indexes = [
            models.Index(fields=['serial_number']),
            models.Index(fields=['distributor', 'is_active']),
        ]
    
    def __str__(self):
        return f"Warranty {self.warranty_number} - {self.serial_number}"


class DistributorPerformance(models.Model):
    """Track distributor performance metrics."""
    
    distributor = models.ForeignKey(
        Distributor,
        on_delete=models.CASCADE,
        related_name='performance_metrics'
    )
    
    # Period
    performance_date = models.DateField(default=timezone.now)
    performance_month = models.IntegerField()  # 1-12
    performance_year = models.IntegerField()
    
    # Sales Metrics
    orders_count = models.IntegerField(default=0)
    total_sales = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    average_order_value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Fulfillment
    on_time_delivery_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    order_accuracy_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    
    # Service Quality
    return_rate_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    complaint_count = models.IntegerField(default=0)
    
    # Payment
    payment_on_time_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    
    # Rating
    RATING_CHOICES = [
        (1, '1 - Poor'),
        (2, '2 - Fair'),
        (3, '3 - Good'),
        (4, '4 - Very Good'),
        (5, '5 - Excellent'),
    ]
    overall_rating = models.IntegerField(
        choices=RATING_CHOICES,
        default=3,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    @classmethod
    def calculate_metrics_for_month(cls, distributor, year, month):
        """
        Calculate all performance metrics for a distributor for a specific month.
        Returns a dictionary with all calculated metrics.
        """
        from django.db.models import Sum, Count, Q, F, Case, When, DecimalField
        from datetime import date
        
        # Get all orders for this distributor in the specified month
        orders = DistributorOrder.objects.filter(
            distributor=distributor,
            order_date__year=year,
            order_date__month=month
        )
        
        # Calculate basic sales metrics
        total_sales = orders.aggregate(Sum('total_amount'))['total_amount__sum'] or Decimal('0')
        orders_count = orders.count()
        average_order_value = (
            total_sales / orders_count if orders_count > 0 else Decimal('0')
        )
        
        # Get shipments for these orders
        shipments = OrderShipment.objects.filter(
            order__in=orders
        )
        
        # Calculate on-time delivery percentage
        total_shipments = shipments.count()
        on_time_shipments = shipments.filter(
            actual_delivery__lte=F('expected_delivery')
        ).count()
        on_time_delivery_percentage = (
            (on_time_shipments / total_shipments * 100) 
            if total_shipments > 0 else Decimal('0')
        )
        
        # Calculate order accuracy (assuming all orders are accurate by default)
        # This can be enhanced with actual accuracy tracking
        order_accuracy_percentage = Decimal('100') if orders_count > 0 else Decimal('0')
        
        # Get after-sales services
        services = AfterSalesService.objects.filter(
            distributor=distributor,
            issue_date__year=year,
            issue_date__month=month
        )
        
        # Calculate return rate and complaint count
        return_rate_percentage = Decimal('0')  # Can be enhanced with return tracking
        complaint_count = services.filter(
            service_type__in=['WARRANTY_CLAIM', 'REPAIR']
        ).count()
        
        # Payment metrics (can be integrated with AR module)
        # For now, assume on-time payment
        payment_on_time_percentage = Decimal('100') if orders_count > 0 else Decimal('0')
        
        # Calculate overall rating (1-5 scale)
        # Based on weighted average of metrics
        overall_rating = cls._calculate_overall_rating(
            on_time_delivery_percentage,
            order_accuracy_percentage,
            return_rate_percentage,
            complaint_count,
            orders_count
        )
        
        return {
            'orders_count': orders_count,
            'total_sales': total_sales,
            'average_order_value': average_order_value,
            'on_time_delivery_percentage': on_time_delivery_percentage,
            'order_accuracy_percentage': order_accuracy_percentage,
            'return_rate_percentage': return_rate_percentage,
            'complaint_count': complaint_count,
            'payment_on_time_percentage': payment_on_time_percentage,
            'overall_rating': overall_rating,
        }
    
    @staticmethod
    def _calculate_overall_rating(on_time_pct, accuracy_pct, return_pct, complaints, orders):
        """
        Calculate overall rating (1-5) based on performance metrics.
        Weighted average calculation.
        """
        if orders == 0:
            return 3  # Default rating
        
        # Weights for each metric
        weights = {
            'on_time': 0.3,
            'accuracy': 0.3,
            'returns': 0.2,
            'complaints': 0.2,
        }
        
        # Normalize metrics to 0-5 scale
        on_time_score = (on_time_pct / 100) * 5
        accuracy_score = (accuracy_pct / 100) * 5
        return_score = max(0, 5 - (return_pct / 100) * 5)  # Lower return % = higher score
        complaint_score = max(0, 5 - min(complaints, 5))  # Max 5 deduction
        
        # Weighted average
        overall = (
            on_time_score * weights['on_time'] +
            accuracy_score * weights['accuracy'] +
            return_score * weights['returns'] +
            complaint_score * weights['complaints']
        )
        
        return min(5, max(1, int(round(overall))))
    
    class Meta:
        db_table = 'manufacturing_distributor_performance'
        ordering = ['-performance_date']
        unique_together = ('distributor', 'performance_month', 'performance_year')
        indexes = [
            models.Index(fields=['distributor', 'performance_date']),
        ]
    
    def __str__(self):
        return f"{self.distributor.distributor_name} - {self.performance_month}/{self.performance_year}"

