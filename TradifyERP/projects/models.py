"""
Project Management Module Models
Complete project management including:
- Project planning & tracking
- Phase management
- Task & resource allocation
- Budget tracking & variance analysis
- Time tracking & timesheets
- Project KPIs & dashboards

Fully integrated with accounting for GL posting.
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal
from accounting.models import Entity, Account, LedgerEntry
from hr.models import Employee, Department


class Project(models.Model):
    """Project master record."""
    
    STATUS_CHOICES = [
        ('PLANNING', 'Planning'),
        ('ACTIVE', 'Active'),
        ('ON_HOLD', 'On Hold'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    PRIORITY_CHOICES = [
        (1, 'Low'),
        (2, 'Medium'),
        (3, 'High'),
        (4, 'Critical'),
    ]
    
    entity = models.ForeignKey(
        Entity,
        on_delete=models.CASCADE,
        related_name='projects'
    )
    
    # Identification
    project_code = models.CharField(max_length=50, unique=True, db_index=True)
    project_name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    # Dates
    start_date = models.DateField()
    planned_end_date = models.DateField()
    actual_end_date = models.DateField(null=True, blank=True)
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PLANNING'
    )
    priority = models.IntegerField(choices=PRIORITY_CHOICES, default=2)
    
    # Ownership
    project_manager = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        related_name='managed_projects'
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='projects'
    )
    
    # Budget
    budgeted_amount = models.DecimalField(max_digits=18, decimal_places=2)
    actual_cost = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    budget_status = models.CharField(
        max_length=20,
        choices=[
            ('ON_BUDGET', 'On Budget'),
            ('OVER_BUDGET', 'Over Budget'),
            ('UNDER_BUDGET', 'Under Budget'),
        ],
        default='ON_BUDGET'
    )
    
    # GL Integration
    project_cost_account = models.ForeignKey(
        Account,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='projects_cost'
    )
    
    # Completion
    completion_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    
    # Audit
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_projects'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['entity', 'status']),
            models.Index(fields=['project_code']),
            models.Index(fields=['start_date']),
        ]
    
    def __str__(self):
        return f"{self.project_code} - {self.project_name}"
    
    @property
    def budget_variance(self):
        """Calculate budget variance."""
        return self.budgeted_amount - self.actual_cost
    
    @property
    def days_remaining(self):
        """Calculate days remaining."""
        if self.actual_end_date:
            return 0
        return (self.planned_end_date - timezone.now().date()).days


class ProjectPhase(models.Model):
    """Project phases/milestones."""
    
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='phases'
    )
    
    # Phase Details
    phase_name = models.CharField(max_length=100)
    sequence = models.IntegerField()
    description = models.TextField(blank=True)
    
    # Dates
    start_date = models.DateField()
    end_date = models.DateField()
    actual_end_date = models.DateField(null=True, blank=True)
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('PENDING', 'Pending'),
            ('IN_PROGRESS', 'In Progress'),
            ('COMPLETED', 'Completed'),
            ('ON_HOLD', 'On Hold'),
        ],
        default='PENDING'
    )
    
    # Budget
    budgeted_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    actual_cost = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    
    # Completion
    completion_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['project', 'sequence']
        unique_together = ('project', 'sequence')
    
    def __str__(self):
        return f"{self.project.project_code} - {self.phase_name}"


class Task(models.Model):
    """Project tasks."""
    
    STATUS_CHOICES = [
        ('TODO', 'To Do'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('BLOCKED', 'Blocked'),
    ]
    
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='tasks'
    )
    
    phase = models.ForeignKey(
        ProjectPhase,
        on_delete=models.CASCADE,
        related_name='tasks'
    )
    
    # Task Details
    task_name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='TODO'
    )
    
    # Dates
    start_date = models.DateField()
    due_date = models.DateField()
    actual_start_date = models.DateField(null=True, blank=True)
    actual_end_date = models.DateField(null=True, blank=True)
    
    # Effort
    estimated_hours = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    actual_hours = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    
    # Budget
    budgeted_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    actual_cost = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    
    # Assignment
    assigned_to = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tasks'
    )
    
    # Completion
    completion_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0
    )
    
    # Dependencies
    depends_on = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='dependent_tasks'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['project', 'phase', 'due_date']
        indexes = [
            models.Index(fields=['project', 'status']),
            models.Index(fields=['assigned_to']),
        ]
    
    def __str__(self):
        return f"{self.project.project_code} - {self.task_name}"
    
    @property
    def is_overdue(self):
        """Check if task is overdue."""
        if self.status != 'COMPLETED':
            return timezone.now().date() > self.due_date
        return False


class ResourceAllocation(models.Model):
    """Resource allocation to projects/tasks."""
    
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='resource_allocations'
    )
    
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='resource_allocations'
    )
    
    # Resource
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='project_allocations'
    )
    
    # Allocation
    allocation_start_date = models.DateField()
    allocation_end_date = models.DateField()
    
    # Hours per week
    hours_per_week = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=40,
        validators=[MinValueValidator(0), MaxValueValidator(168)]
    )
    
    # Rate
    hourly_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    
    # Status
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['allocation_start_date']
        unique_together = ('project', 'employee', 'allocation_start_date')
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.project.project_code}"


class ProjectBudget(models.Model):
    """Project budget breakdown by category."""
    
    BUDGET_CATEGORIES = [
        ('LABOR', 'Labor'),
        ('MATERIAL', 'Material'),
        ('EQUIPMENT', 'Equipment'),
        ('OVERHEAD', 'Overhead'),
        ('CONTINGENCY', 'Contingency'),
        ('OTHER', 'Other'),
    ]
    
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='budget_lines'
    )
    
    # Category
    category = models.CharField(max_length=20, choices=BUDGET_CATEGORIES)
    description = models.CharField(max_length=255)
    
    # Budget
    budgeted_amount = models.DecimalField(max_digits=18, decimal_places=2)
    actual_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    committed_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0,
        help_text="Amount committed but not yet spent"
    )
    
    # GL Account
    gl_account = models.ForeignKey(
        Account,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='project_budgets'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['project', 'category']
        unique_together = ('project', 'category')
    
    def __str__(self):
        return f"{self.project.project_code} - {self.category}"
    
    @property
    def available_budget(self):
        """Calculate available budget."""
        return self.budgeted_amount - self.actual_amount - self.committed_amount
    
    @property
    def budget_variance(self):
        """Calculate budget variance."""
        return self.budgeted_amount - (self.actual_amount + self.committed_amount)


class TimeEntry(models.Model):
    """Time tracking entries."""
    
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='time_entries'
    )
    
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='time_entries'
    )
    
    # Employee
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='project_time_entries'
    )
    
    # Date & Hours
    entry_date = models.DateField()
    hours_worked = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    
    # Description
    description = models.TextField()
    
    # Cost
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2)
    cost = models.DecimalField(max_digits=18, decimal_places=2)
    
    # Status
    is_billable = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-entry_date']
        indexes = [
            models.Index(fields=['project', 'entry_date']),
            models.Index(fields=['employee', 'entry_date']),
        ]
    
    def save(self, *args, **kwargs):
        """Auto-calculate cost."""
        self.cost = self.hours_worked * self.hourly_rate
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.project.project_code} - {self.entry_date}"


class ProjectKPI(models.Model):
    """Project KPIs and metrics."""
    
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='kpis'
    )
    
    # KPI Details
    kpi_name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    # Metrics
    target_value = models.DecimalField(max_digits=18, decimal_places=2)
    actual_value = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    unit = models.CharField(max_length=50)  # %, hours, $, etc.
    
    # Date
    measurement_date = models.DateField(default=timezone.now)
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('ON_TRACK', 'On Track'),
            ('AT_RISK', 'At Risk'),
            ('OFF_TRACK', 'Off Track'),
        ],
        default='ON_TRACK'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['project', 'measurement_date']
    
    def __str__(self):
        return f"{self.project.project_code} - {self.kpi_name}"


class ProjectSettings(models.Model):
    """Project management settings per entity."""
    
    entity = models.OneToOneField(
        Entity,
        on_delete=models.CASCADE,
        related_name='project_settings'
    )
    
    # Policies
    require_budget_approval = models.BooleanField(default=True)
    budget_approval_threshold = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    
    # Time Tracking
    require_time_entry = models.BooleanField(default=True)
    billable_rate_default = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Project Codes
    project_code_prefix = models.CharField(max_length=10, default='PRJ')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Project Settings - {self.entity.code}"
