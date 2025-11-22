from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from accounting.models import Entity
from django.contrib.auth.models import User


# ==================== Asset Management ====================

class MaintenanceAsset(models.Model):
    """Track all equipment, machines, and infrastructure at the site."""
    
    ASSET_TYPE_CHOICES = [
        ('EQUIPMENT', 'Equipment'),
        ('MACHINE', 'Machine'),
        ('INFRASTRUCTURE', 'Infrastructure'),
        ('VEHICLE', 'Vehicle'),
        ('BUILDING', 'Building'),
        ('HVAC', 'HVAC System'),
        ('ELECTRICAL', 'Electrical System'),
        ('PLUMBING', 'Plumbing System'),
        ('OTHER', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('OPERATIONAL', 'Operational'),
        ('IDLE', 'Idle'),
        ('MAINTENANCE', 'Under Maintenance'),
        ('RETIRED', 'Retired'),
    ]
    
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE, related_name='maintenance_assets', null=True, blank=True)
    asset_code = models.CharField(max_length=50, unique=True)
    asset_name = models.CharField(max_length=255)
    asset_type = models.CharField(max_length=50, choices=ASSET_TYPE_CHOICES)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=255)
    manufacturer = models.CharField(max_length=255, blank=True)
    model = models.CharField(max_length=255, blank=True)
    serial_number = models.CharField(max_length=255, blank=True, unique=True)
    purchase_date = models.DateField()
    acquisition_cost = models.DecimalField(max_digits=15, decimal_places=2)
    warranty_expiry = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='OPERATIONAL')
    operational_hours = models.IntegerField(default=0)
    last_maintenance_date = models.DateField(blank=True, null=True)
    next_scheduled_maintenance = models.DateField(blank=True, null=True)
    critical_asset = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'maintenance_asset'
        ordering = ['asset_code']
        indexes = [
            models.Index(fields=['entity', 'status']),
            models.Index(fields=['asset_type']),
        ]
    
    def __str__(self):
        return f"{self.asset_code} - {self.asset_name}"


# ==================== Maintenance Tasks ====================

class MaintenanceTask(models.Model):
    """Define preventive and corrective maintenance tasks."""
    
    TASK_TYPE_CHOICES = [
        ('PREVENTIVE', 'Preventive'),
        ('CORRECTIVE', 'Corrective'),
        ('EMERGENCY', 'Emergency'),
    ]
    
    FREQUENCY_CHOICES = [
        ('DAILY', 'Daily'),
        ('WEEKLY', 'Weekly'),
        ('BIWEEKLY', 'Bi-weekly'),
        ('MONTHLY', 'Monthly'),
        ('QUARTERLY', 'Quarterly'),
        ('SEMI_ANNUAL', 'Semi-annual'),
        ('ANNUAL', 'Annual'),
        ('AS_NEEDED', 'As Needed'),
    ]
    
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE, related_name='maintenance_tasks', null=True, blank=True)
    asset = models.ForeignKey(MaintenanceAsset, on_delete=models.CASCADE, related_name='maintenance_tasks')
    task_code = models.CharField(max_length=50)
    task_name = models.CharField(max_length=255)
    task_type = models.CharField(max_length=20, choices=TASK_TYPE_CHOICES)
    description = models.TextField()
    instructions = models.TextField(blank=True)
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES)
    estimated_duration_hours = models.DecimalField(max_digits=6, decimal_places=2)
    estimated_cost = models.DecimalField(max_digits=12, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'maintenance_task'
        ordering = ['asset', 'task_code']
        unique_together = ['asset', 'task_code']
    
    def __str__(self):
        return f"{self.task_code} - {self.task_name}"


# ==================== Work Order Management ====================

class WorkOrder(models.Model):
    """Create, assign, and track maintenance jobs."""
    
    PRIORITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    ]
    
    STATUS_CHOICES = [
        ('PLANNED', 'Planned'),
        ('ASSIGNED', 'Assigned'),
        ('IN_PROGRESS', 'In Progress'),
        ('ON_HOLD', 'On Hold'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE, related_name='work_orders', null=True, blank=True)
    work_order_number = models.CharField(max_length=50, unique=True)
    maintenance_task = models.ForeignKey(MaintenanceTask, on_delete=models.SET_NULL, null=True, blank=True)
    asset = models.ForeignKey(MaintenanceAsset, on_delete=models.CASCADE, related_name='work_orders')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='MEDIUM')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PLANNED')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_work_orders')
    description = models.TextField()
    scheduled_date = models.DateField()
    scheduled_start_time = models.TimeField(blank=True, null=True)
    scheduled_end_time = models.TimeField(blank=True, null=True)
    actual_start_date = models.DateTimeField(blank=True, null=True)
    actual_end_date = models.DateTimeField(blank=True, null=True)
    estimated_hours = models.DecimalField(max_digits=6, decimal_places=2)
    actual_hours = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    estimated_cost = models.DecimalField(max_digits=12, decimal_places=2)
    actual_cost = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'maintenance_work_order'
        ordering = ['-scheduled_date', '-priority']
        indexes = [
            models.Index(fields=['entity', 'status']),
            models.Index(fields=['asset', 'status']),
        ]
    
    def __str__(self):
        return f"{self.work_order_number} - {self.asset.asset_name}"


# ==================== Spare Parts & Inventory ====================

class SparePart(models.Model):
    """Manage spare parts inventory linked to maintenance tasks."""
    
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE, related_name='spare_parts', null=True, blank=True)
    part_code = models.CharField(max_length=50, unique=True)
    part_name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    unit_cost = models.DecimalField(max_digits=12, decimal_places=2)
    current_stock = models.IntegerField(default=0)
    reorder_level = models.IntegerField()
    reorder_quantity = models.IntegerField()
    warehouse_location = models.CharField(max_length=255, blank=True)
    supplier = models.CharField(max_length=255, blank=True)
    lead_time_days = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'maintenance_spare_part'
        ordering = ['part_code']
    
    def __str__(self):
        return f"{self.part_code} - {self.part_name}"
    
    def needs_reorder(self):
        return self.current_stock <= self.reorder_level


class WorkOrderSparePart(models.Model):
    """Link spare parts to work orders."""
    
    work_order = models.ForeignKey(WorkOrder, on_delete=models.CASCADE, related_name='spare_parts_used')
    spare_part = models.ForeignKey(SparePart, on_delete=models.CASCADE)
    quantity_used = models.IntegerField()
    unit_cost = models.DecimalField(max_digits=12, decimal_places=2)
    total_cost = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'maintenance_work_order_spare_part'
        unique_together = ['work_order', 'spare_part']
    
    def __str__(self):
        return f"{self.work_order.work_order_number} - {self.spare_part.part_code}"


# ==================== Vendor & Contractor Management ====================

class MaintenanceVendor(models.Model):
    """Track external service providers and contractors."""
    
    VENDOR_TYPE_CHOICES = [
        ('CONTRACTOR', 'Contractor'),
        ('SUPPLIER', 'Supplier'),
        ('SERVICE_PROVIDER', 'Service Provider'),
        ('CONSULTANT', 'Consultant'),
    ]
    
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE, related_name='maintenance_vendors', null=True, blank=True)
    vendor_code = models.CharField(max_length=50, unique=True)
    vendor_name = models.CharField(max_length=255)
    vendor_type = models.CharField(max_length=30, choices=VENDOR_TYPE_CHOICES)
    contact_person = models.CharField(max_length=255, blank=True)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    website = models.URLField(blank=True)
    service_areas = models.TextField(help_text="Comma-separated service categories")
    performance_rating = models.DecimalField(max_digits=3, decimal_places=2, default=3.0, 
                                           validators=[MinValueValidator(0), MaxValueValidator(5)])
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'maintenance_vendor'
        ordering = ['vendor_code']
    
    def __str__(self):
        return f"{self.vendor_code} - {self.vendor_name}"


class VendorContract(models.Model):
    """Track vendor contracts and SLAs."""
    
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'),
        ('EXPIRED', 'Expired'),
        ('PENDING_RENEWAL', 'Pending Renewal'),
    ]
    
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE, related_name='vendor_contracts', null=True, blank=True)
    vendor = models.ForeignKey(MaintenanceVendor, on_delete=models.CASCADE, related_name='contracts')
    contract_number = models.CharField(max_length=50, unique=True)
    description = models.TextField()
    contract_value = models.DecimalField(max_digits=15, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField()
    service_level_agreement = models.TextField(blank=True)
    response_time_hours = models.IntegerField(default=24)
    resolution_time_hours = models.IntegerField(default=72)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'maintenance_vendor_contract'
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.contract_number} - {self.vendor.vendor_name}"


# ==================== Safety & Compliance ====================

class ComplianceStandard(models.Model):
    """Define regulatory and safety standards."""
    
    STANDARD_TYPE_CHOICES = [
        ('OSHA', 'OSHA'),
        ('ISO', 'ISO'),
        ('EPA', 'EPA'),
        ('NFPA', 'NFPA'),
        ('INDUSTRY', 'Industry-specific'),
        ('INTERNAL', 'Internal Policy'),
    ]
    
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE, related_name='compliance_standards', null=True, blank=True)
    standard_code = models.CharField(max_length=50)
    standard_name = models.CharField(max_length=255)
    standard_type = models.CharField(max_length=30, choices=STANDARD_TYPE_CHOICES)
    description = models.TextField()
    requirements = models.TextField()
    audit_frequency_months = models.IntegerField(default=12)
    is_mandatory = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'maintenance_compliance_standard'
        unique_together = ['entity', 'standard_code']
    
    def __str__(self):
        return f"{self.standard_code} - {self.standard_name}"


class ComplianceAudit(models.Model):
    """Track compliance audits and certifications."""
    
    STATUS_CHOICES = [
        ('PLANNED', 'Planned'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]
    
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE, related_name='compliance_audits', null=True, blank=True)
    standard = models.ForeignKey(ComplianceStandard, on_delete=models.CASCADE)
    audit_date = models.DateField()
    auditor_name = models.CharField(max_length=255)
    audit_result = models.CharField(max_length=20, choices=STATUS_CHOICES)
    findings = models.TextField(blank=True)
    corrective_actions = models.TextField(blank=True)
    next_audit_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'maintenance_compliance_audit'
        ordering = ['-audit_date']
    
    def __str__(self):
        return f"{self.standard.standard_code} - {self.audit_date}"


# ==================== Cost Tracking ====================

class MaintenanceCost(models.Model):
    """Record labor, parts, and downtime costs."""
    
    COST_TYPE_CHOICES = [
        ('LABOR', 'Labor'),
        ('PARTS', 'Parts'),
        ('EQUIPMENT', 'Equipment'),
        ('DOWNTIME', 'Downtime'),
        ('VENDOR_SERVICE', 'Vendor Service'),
        ('OTHER', 'Other'),
    ]
    
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE, related_name='maintenance_costs', null=True, blank=True)
    work_order = models.ForeignKey(WorkOrder, on_delete=models.CASCADE, related_name='costs')
    cost_type = models.CharField(max_length=30, choices=COST_TYPE_CHOICES)
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    cost_date = models.DateField()
    assigned_to = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'maintenance_cost'
        ordering = ['-cost_date']
        indexes = [
            models.Index(fields=['work_order', 'cost_type']),
        ]
    
    def __str__(self):
        return f"{self.work_order.work_order_number} - {self.cost_type}: {self.amount}"


class DowntimeRecord(models.Model):
    """Track equipment downtime and impact."""
    
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE, related_name='downtime_records', null=True, blank=True)
    asset = models.ForeignKey(MaintenanceAsset, on_delete=models.CASCADE, related_name='downtime_records')
    work_order = models.ForeignKey(WorkOrder, on_delete=models.CASCADE, related_name='downtime_records')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    duration_hours = models.DecimalField(max_digits=8, decimal_places=2)
    reason = models.CharField(max_length=255)
    production_loss_estimate = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    affected_processes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'maintenance_downtime_record'
        ordering = ['-start_time']
    
    def __str__(self):
        return f"{self.asset.asset_name} - {self.start_time}"
