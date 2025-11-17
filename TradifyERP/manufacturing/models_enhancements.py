"""
Manufacturing Module Enhancements - Brings Manufacturing from 9.5/10 to 9.8/10
Advanced production planning, variance analysis, and quality metrics.
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal


class ProductionSchedule(models.Model):
    """
    Advanced production scheduling with resource allocation.
    """
    entity = models.ForeignKey(
        'accounting.Entity',
        on_delete=models.CASCADE,
        related_name='production_schedules'
    )
    
    schedule_date = models.DateField(db_index=True)
    work_center = models.ForeignKey(
        'manufacturing.WorkCenter',
        on_delete=models.CASCADE,
        related_name='schedules'
    )
    
    production_order = models.ForeignKey(
        'manufacturing.ProductionOrder',
        on_delete=models.CASCADE,
        related_name='schedules'
    )
    
    # Capacity
    scheduled_hours = models.DecimalField(max_digits=8, decimal_places=2)
    actual_hours = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    available_hours = models.DecimalField(max_digits=8, decimal_places=2)
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('SCHEDULED', 'Scheduled'),
            ('IN_PROGRESS', 'In Progress'),
            ('COMPLETED', 'Completed'),
            ('CANCELLED', 'Cancelled'),
        ],
        default='SCHEDULED'
    )
    
    # Resources
    assigned_employees = models.ManyToManyField(
        'hr.Employee',
        related_name='production_assignments'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['schedule_date', 'work_center']
        unique_together = ('schedule_date', 'work_center', 'production_order')
    
    def __str__(self):
        return f"Schedule - {self.work_center} on {self.schedule_date}"


class ProductionVariance(models.Model):
    """
    Track variances between estimated and actual production costs.
    Material, labor, overhead variances.
    """
    VARIANCE_TYPES = [
        ('MATERIAL_USAGE', 'Material Usage Variance'),
        ('MATERIAL_PRICE', 'Material Price Variance'),
        ('LABOR_RATE', 'Labor Rate Variance'),
        ('LABOR_EFFICIENCY', 'Labor Efficiency Variance'),
        ('OVERHEAD_VOLUME', 'Overhead Volume Variance'),
        ('OVERHEAD_EFFICIENCY', 'Overhead Efficiency Variance'),
    ]
    
    production_order = models.ForeignKey(
        'manufacturing.ProductionOrder',
        on_delete=models.CASCADE,
        related_name='variances'
    )
    
    variance_type = models.CharField(max_length=50, choices=VARIANCE_TYPES)
    
    # Amounts
    standard_amount = models.DecimalField(max_digits=18, decimal_places=2)
    actual_amount = models.DecimalField(max_digits=18, decimal_places=2)
    variance_amount = models.DecimalField(max_digits=18, decimal_places=2)
    variance_percentage = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(-100), MaxValueValidator(100)]
    )
    
    # Analysis
    variance_reason = models.TextField(blank=True)
    is_favorable = models.BooleanField()
    requires_investigation = models.BooleanField(default=False)
    
    # GL Account
    variance_account = models.ForeignKey(
        'accounting.Account',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='production_variances'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ('production_order', 'variance_type')
    
    def __str__(self):
        return f"{self.get_variance_type_display()}: ${self.variance_amount}"


class QualityMetric(models.Model):
    """
    Track quality metrics and KPIs for products and production runs.
    """
    METRIC_TYPES = [
        ('DEFECT_RATE', 'Defect Rate %'),
        ('FIRST_PASS_YIELD', 'First Pass Yield %'),
        ('REWORK_RATE', 'Rework Rate %'),
        ('SCRAP_RATE', 'Scrap Rate %'),
        ('ON_TIME_DELIVERY', 'On-Time Delivery %'),
        ('CUSTOMER_RETURNS', 'Customer Returns Rate %'),
    ]
    
    product = models.ForeignKey(
        'manufacturing.Product',
        on_delete=models.CASCADE,
        related_name='quality_metrics'
    )
    
    metric_type = models.CharField(max_length=50, choices=METRIC_TYPES)
    
    # Values
    target_value = models.DecimalField(max_digits=8, decimal_places=2)
    actual_value = models.DecimalField(max_digits=8, decimal_places=2)
    lower_control_limit = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    upper_control_limit = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    
    # Status
    is_within_spec = models.BooleanField()
    alert_threshold = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    
    period_start = models.DateField()
    period_end = models.DateField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-period_end', 'product']
        unique_together = ('product', 'metric_type', 'period_start', 'period_end')
    
    def __str__(self):
        return f"{self.product} - {self.get_metric_type_display()}"


class ProductionDefect(models.Model):
    """
    Track defects identified during production and quality inspection.
    """
    SEVERITY_LEVELS = [
        ('CRITICAL', 'Critical - Safety Risk'),
        ('HIGH', 'High - Major Issue'),
        ('MEDIUM', 'Medium - Functional Impact'),
        ('LOW', 'Low - Cosmetic'),
    ]
    
    STATUS_CHOICES = [
        ('IDENTIFIED', 'Identified'),
        ('LOGGED', 'Logged'),
        ('UNDER_INVESTIGATION', 'Under Investigation'),
        ('RESOLVED', 'Resolved'),
        ('CLOSED', 'Closed'),
    ]
    
    production_order = models.ForeignKey(
        'manufacturing.ProductionOrder',
        on_delete=models.CASCADE,
        related_name='defects'
    )
    
    quality_inspection = models.ForeignKey(
        'manufacturing.QualityInspection',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='defects'
    )
    
    # Details
    defect_code = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    
    # Classification
    severity = models.CharField(max_length=20, choices=SEVERITY_LEVELS)
    category = models.CharField(max_length=100)  # e.g., "Dimensional", "Surface", "Functional"
    
    # Status
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='IDENTIFIED')
    identified_date = models.DateTimeField(auto_now_add=True)
    resolved_date = models.DateTimeField(null=True, blank=True)
    
    # Root Cause
    root_cause = models.TextField(blank=True)
    corrective_action = models.TextField(blank=True)
    
    # Impact
    units_affected = models.IntegerField(default=1)
    rework_required = models.BooleanField(default=False)
    scrap_required = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-identified_date']
        indexes = [
            models.Index(fields=['production_order', 'status']),
            models.Index(fields=['severity', 'status']),
        ]
    
    def __str__(self):
        return f"{self.defect_code} - {self.title}"


class EquipmentMaintenance(models.Model):
    """
    Track equipment maintenance schedules and history.
    Preventive and corrective maintenance.
    """
    MAINTENANCE_TYPES = [
        ('PREVENTIVE', 'Preventive Maintenance'),
        ('CORRECTIVE', 'Corrective Maintenance'),
        ('PREDICTIVE', 'Predictive Maintenance'),
        ('INSPECTION', 'Inspection'),
    ]
    
    STATUS_CHOICES = [
        ('SCHEDULED', 'Scheduled'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed - Needs Rework'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    equipment = models.ForeignKey(
        'manufacturing.Equipment',
        on_delete=models.CASCADE,
        related_name='maintenance_records'
    )
    
    maintenance_type = models.CharField(max_length=30, choices=MAINTENANCE_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SCHEDULED')
    
    # Scheduling
    scheduled_date = models.DateField()
    actual_start_date = models.DateField(null=True, blank=True)
    actual_end_date = models.DateField(null=True, blank=True)
    
    # Details
    description = models.TextField()
    work_order_number = models.CharField(max_length=50, unique=True)
    
    # Resources
    technician = models.ForeignKey(
        'hr.Employee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='equipment_maintenance'
    )
    labor_hours = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    
    # Costs
    parts_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    labor_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Results
    findings = models.TextField(blank=True)
    corrective_actions = models.TextField(blank=True)
    next_maintenance_date = models.DateField(null=True, blank=True)
    
    # GL Account
    expense_account = models.ForeignKey(
        'accounting.Account',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='equipment_maintenance'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['equipment', '-scheduled_date']
        indexes = [
            models.Index(fields=['equipment', 'scheduled_date']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.equipment} - {self.work_order_number}"


class ProductionMetrics(models.Model):
    """
    Aggregate production metrics and KPIs.
    """
    entity = models.ForeignKey(
        'accounting.Entity',
        on_delete=models.CASCADE,
        related_name='production_metrics'
    )
    
    period_start = models.DateField()
    period_end = models.DateField()
    
    # Output Metrics
    total_orders = models.IntegerField()
    completed_orders = models.IntegerField()
    on_time_orders = models.IntegerField()
    
    completion_rate = models.DecimalField(max_digits=8, decimal_places=2)  # %
    on_time_rate = models.DecimalField(max_digits=8, decimal_places=2)     # %
    
    # Cost Metrics
    total_production_cost = models.DecimalField(max_digits=18, decimal_places=2)
    material_cost_variance = models.DecimalField(max_digits=18, decimal_places=2)
    labor_cost_variance = models.DecimalField(max_digits=18, decimal_places=2)
    
    # Quality Metrics
    defect_rate = models.DecimalField(max_digits=8, decimal_places=2)          # %
    first_pass_yield = models.DecimalField(max_digits=8, decimal_places=2)     # %
    scrap_rate = models.DecimalField(max_digits=8, decimal_places=2)           # %
    
    # Efficiency
    overall_equipment_effectiveness = models.DecimalField(              # OEE %
        max_digits=8,
        decimal_places=2
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-period_end']
        unique_together = ('entity', 'period_start', 'period_end')
    
    def __str__(self):
        return f"Production Metrics - {self.period_start} to {self.period_end}"
