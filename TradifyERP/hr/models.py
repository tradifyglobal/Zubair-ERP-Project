"""
HR Module Models
Fully integrated with accounting for payroll, benefits, and tax compliance.
Implements industry best practices for employee lifecycle management.
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal
import uuid


class Department(models.Model):
    """
    Organizational departments/cost centers.
    Links to GL accounts for cost allocation.
    """
    entity = models.ForeignKey(
        'accounting.Entity',
        on_delete=models.CASCADE,
        related_name='hr_departments'
    )
    
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    
    # GL Integration
    cost_center_account = models.ForeignKey(
        'accounting.Account',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='departments',
        help_text="Cost center account for expense allocation"
    )
    
    # Management
    manager = models.ForeignKey(
        'Employee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_departments',
        help_text="Department manager"
    )
    
    # Budget
    annual_budget = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    
    # Status
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        unique_together = ('entity', 'code')
    
    def __str__(self):
        return f"{self.name} ({self.code})"


class Position(models.Model):
    """
    Job positions/roles with salary grades.
    """
    EMPLOYMENT_TYPES = [
        ('FULL_TIME', 'Full-time'),
        ('PART_TIME', 'Part-time'),
        ('CONTRACT', 'Contract'),
        ('TEMPORARY', 'Temporary'),
        ('INTERN', 'Intern'),
    ]
    
    entity = models.ForeignKey(
        'accounting.Entity',
        on_delete=models.CASCADE,
        related_name='hr_positions'
    )
    
    title = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='positions'
    )
    
    # Compensation
    employment_type = models.CharField(
        max_length=20,
        choices=EMPLOYMENT_TYPES,
        default='FULL_TIME'
    )
    salary_grade = models.CharField(max_length=20)
    min_salary = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    max_salary = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    
    # GL Accounts for expense posting
    salary_expense_account = models.ForeignKey(
        'accounting.Account',
        on_delete=models.PROTECT,
        related_name='positions_salary',
        help_text="Expense account for salary posting"
    )
    
    # Reporting
    reports_to = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='direct_reports'
    )
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['title']
        unique_together = ('entity', 'code')
    
    def __str__(self):
        return f"{self.title} ({self.salary_grade})"


class Employee(models.Model):
    """
    Core employee master data with GL integration.
    """
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'),
        ('ON_LEAVE', 'On Leave'),
        ('TERMINATED', 'Terminated'),
    ]
    
    entity = models.ForeignKey(
        'accounting.Entity',
        on_delete=models.CASCADE,
        related_name='hr_employees'
    )
    
    # ID & Personal
    employee_id = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,
        help_text="Unique employee identifier"
    )
    user = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='hr_employee'
    )
    
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True, db_index=True)
    phone = models.CharField(max_length=20, blank=True)
    
    # Tax & Legal
    ssn = models.CharField(
        max_length=20,
        unique=True,
        help_text="Social Security Number or equivalent"
    )
    tax_id = models.CharField(
        max_length=50,
        blank=True,
        help_text="Tax identification number"
    )
    
    # Employment Details
    position = models.ForeignKey(
        Position,
        on_delete=models.SET_NULL,
        null=True,
        related_name='employees'
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        related_name='employees'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='ACTIVE'
    )
    
    # Dates
    hire_date = models.DateField()
    termination_date = models.DateField(null=True, blank=True)
    
    # Compensation
    base_salary = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    salary_currency = models.CharField(
        max_length=3,
        default='USD'
    )
    pay_frequency = models.CharField(
        max_length=20,
        choices=[
            ('WEEKLY', 'Weekly'),
            ('BIWEEKLY', 'Bi-weekly'),
            ('MONTHLY', 'Monthly'),
            ('ANNUALLY', 'Annually'),
        ],
        default='MONTHLY'
    )
    
    # GL Accounts (for auto-posting payroll)
    payroll_account = models.ForeignKey(
        'accounting.Account',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employees_payroll',
        help_text="GL account for salary expense posting"
    )
    
    # Manager
    manager = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='direct_reports',
        limit_choices_to={'status': 'ACTIVE'}
    )
    
    # Contact Info
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=50, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True)
    
    # Audit
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_employees'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['last_name', 'first_name']
        indexes = [
            models.Index(fields=['employee_id']),
            models.Index(fields=['entity', 'status']),
            models.Index(fields=['department']),
        ]
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.employee_id})"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def is_employed(self):
        """Check if employee is currently employed."""
        return self.status in ['ACTIVE', 'ON_LEAVE']


class Payroll(models.Model):
    """
    Payroll run/cycle master record.
    """
    PAYROLL_STATUS = [
        ('DRAFT', 'Draft'),
        ('SUBMITTED', 'Submitted'),
        ('APPROVED', 'Approved'),
        ('PROCESSED', 'Processed'),
        ('PAID', 'Paid'),
        ('REVERSED', 'Reversed'),
    ]
    
    entity = models.ForeignKey(
        'accounting.Entity',
        on_delete=models.CASCADE,
        related_name='hr_payrolls'
    )
    
    # Period
    payroll_number = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        help_text="Unique payroll identifier (e.g., PAY-2025-01)"
    )
    payroll_date = models.DateField(
        db_index=True,
        help_text="Payroll payment date"
    )
    period_start = models.DateField()
    period_end = models.DateField()
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=PAYROLL_STATUS,
        default='DRAFT'
    )
    
    # Totals
    total_gross = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0
    )
    total_deductions = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0
    )
    total_taxes = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0
    )
    total_net = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0
    )
    
    # GL Posting
    is_posted = models.BooleanField(
        default=False,
        help_text="Whether payroll has been posted to GL"
    )
    posted_date = models.DateTimeField(null=True, blank=True)
    posted_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='posted_payrolls'
    )
    
    # Approvals
    submitted_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='submitted_payrolls'
    )
    submitted_date = models.DateTimeField(null=True, blank=True)
    
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_payrolls'
    )
    approved_date = models.DateTimeField(null=True, blank=True)
    
    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-payroll_date']
        indexes = [
            models.Index(fields=['entity', 'payroll_date']),
            models.Index(fields=['status']),
        ]
        unique_together = ('entity', 'payroll_number')
    
    def __str__(self):
        return f"{self.payroll_number} - {self.payroll_date.strftime('%B %Y')}"
    
    def calculate_totals(self):
        """Recalculate payroll totals from pay records."""
        self.total_gross = sum(
            pr.gross_amount for pr in self.payroll_records.all()
        )
        self.total_deductions = sum(
            pr.total_deductions for pr in self.payroll_records.all()
        )
        self.total_taxes = sum(
            pr.total_taxes for pr in self.payroll_records.all()
        )
        self.total_net = sum(
            pr.net_amount for pr in self.payroll_records.all()
        )
        self.save()


class PayrollRecord(models.Model):
    """
    Individual employee payroll record (one per employee per payroll).
    """
    payroll = models.ForeignKey(
        Payroll,
        on_delete=models.CASCADE,
        related_name='payroll_records'
    )
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='payroll_records'
    )
    
    # Pay Calculation
    days_worked = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('20'),
        validators=[MinValueValidator(0), MaxValueValidator(31)]
    )
    hours_worked = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=Decimal('160'),
        validators=[MinValueValidator(0)]
    )
    
    # Earnings
    base_salary = models.DecimalField(max_digits=18, decimal_places=2)
    overtime_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0,
        help_text="Additional pay for overtime"
    )
    bonus = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0
    )
    allowances = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0,
        help_text="Housing, transportation, etc."
    )
    
    gross_amount = models.DecimalField(max_digits=18, decimal_places=2)
    
    # Deductions
    employee_tax = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0,
        help_text="Income tax deduction"
    )
    social_security = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0,
        help_text="Social security/pension contribution"
    )
    health_insurance = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0
    )
    other_deductions = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0
    )
    total_deductions = models.DecimalField(max_digits=18, decimal_places=2)
    
    # Tax
    total_taxes = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0
    )
    
    # Net
    net_amount = models.DecimalField(max_digits=18, decimal_places=2)
    
    # Employer Costs
    employer_tax = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0,
        help_text="Employer share of taxes"
    )
    employer_contribution = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0,
        help_text="Employer contribution to benefits"
    )
    
    # Notes
    notes = models.TextField(blank=True)
    
    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('payroll', 'employee')
        ordering = ['employee__last_name']
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.payroll.payroll_date.strftime('%b %Y')}"
    
    def calculate(self):
        """Calculate all payroll amounts."""
        # Calculate gross
        self.gross_amount = (
            self.base_salary + self.overtime_amount + self.bonus + self.allowances
        )
        
        # Calculate total deductions
        self.total_deductions = (
            self.employee_tax + self.social_security + 
            self.health_insurance + self.other_deductions
        )
        
        # Calculate total taxes (income tax + contributions counted as tax)
        self.total_taxes = self.employee_tax + self.social_security
        
        # Calculate net
        self.net_amount = self.gross_amount - self.total_deductions
        
        self.save()


class Benefit(models.Model):
    """
    Employee benefits (health insurance, 401k, etc.).
    """
    BENEFIT_TYPES = [
        ('HEALTH_INSURANCE', 'Health Insurance'),
        ('DENTAL', 'Dental Plan'),
        ('VISION', 'Vision Plan'),
        ('401K', '401(k) Retirement'),
        ('STOCK_OPTION', 'Stock Options'),
        ('LIFE_INSURANCE', 'Life Insurance'),
        ('DISABILITY', 'Disability Insurance'),
        ('FSA', 'Flexible Spending Account'),
        ('HSA', 'Health Savings Account'),
        ('TUITION_REIMBURSEMENT', 'Tuition Reimbursement'),
        ('OTHER', 'Other'),
    ]
    
    entity = models.ForeignKey(
        'accounting.Entity',
        on_delete=models.CASCADE,
        related_name='hr_benefits'
    )
    
    name = models.CharField(max_length=100)
    benefit_type = models.CharField(max_length=50, choices=BENEFIT_TYPES)
    description = models.TextField(blank=True)
    
    # Cost Tracking
    employee_cost = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        help_text="Cost to employee per period"
    )
    employer_cost = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        help_text="Cost to employer per period"
    )
    
    # GL Accounts
    employee_expense_account = models.ForeignKey(
        'accounting.Account',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='benefits_employee_expense'
    )
    employer_expense_account = models.ForeignKey(
        'accounting.Account',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='benefits_employer_expense'
    )
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['benefit_type', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.get_benefit_type_display()})"


class EmployeeBenefit(models.Model):
    """
    Track which employees are enrolled in which benefits.
    """
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='enrolled_benefits'
    )
    benefit = models.ForeignKey(
        Benefit,
        on_delete=models.CASCADE,
        related_name='enrollments'
    )
    
    # Enrollment Details
    enrollment_date = models.DateField()
    termination_date = models.DateField(null=True, blank=True)
    
    # Custom costs (override benefit default if needed)
    employee_contribution = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        null=True,
        blank=True
    )
    employer_contribution = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('employee', 'benefit')
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.benefit.name}"


class Leave(models.Model):
    """
    Leave type master (Vacation, Sick, etc.).
    """
    entity = models.ForeignKey(
        'accounting.Entity',
        on_delete=models.CASCADE,
        related_name='hr_leave_types'
    )
    
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    
    # Accrual
    annual_allocation = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Days allocated per year"
    )
    accrual_method = models.CharField(
        max_length=20,
        choices=[
            ('ANNUAL', 'Annual (all at once)'),
            ('MONTHLY', 'Monthly accrual'),
            ('QUARTERLY', 'Quarterly accrual'),
        ],
        default='ANNUAL'
    )
    can_carry_over = models.BooleanField(
        default=False,
        help_text="Can unused days roll over to next year?"
    )
    max_carryover = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text="Maximum days that can carry over"
    )
    
    # Restrictions
    requires_approval = models.BooleanField(default=True)
    notice_days_required = models.IntegerField(default=1)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class LeaveBalance(models.Model):
    """
    Track leave balance per employee per year.
    """
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='leave_balances'
    )
    leave_type = models.ForeignKey(
        Leave,
        on_delete=models.CASCADE,
        related_name='employee_balances'
    )
    year = models.IntegerField(db_index=True)
    
    # Balance Tracking
    opening_balance = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Balance from previous year"
    )
    allocated = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Allocated this year"
    )
    taken = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text="Already taken this year"
    )
    forfeited = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text="Forfeited this year"
    )
    
    @property
    def available(self):
        """Calculate available leave days."""
        return self.opening_balance + self.allocated - self.taken - self.forfeited
    
    @property
    def pending(self):
        """Calculate pending leave days (approved but not yet taken)."""
        return self.leave_requests.filter(
            status='APPROVED',
            start_date__year=self.year
        ).aggregate(
            total=models.Sum('duration')
        )['total'] or 0
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('employee', 'leave_type', 'year')
        ordering = ['year', 'leave_type']
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.leave_type.name} ({self.year})"


class LeaveRequest(models.Model):
    """
    Track employee leave requests.
    """
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('SUBMITTED', 'Submitted'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='leave_requests'
    )
    leave_type = models.ForeignKey(
        Leave,
        on_delete=models.CASCADE,
        related_name='requests'
    )
    
    # Request Details
    start_date = models.DateField()
    end_date = models.DateField()
    duration = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Duration in days"
    )
    
    reason = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='DRAFT'
    )
    
    # Approval
    submitted_date = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_leave_requests'
    )
    approval_date = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    
    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.leave_type.name} ({self.start_date})"


class Performance(models.Model):
    """
    Employee performance reviews and ratings.
    """
    RATING_CHOICES = [
        (1, 'Below Expectations'),
        (2, 'Meets Expectations'),
        (3, 'Exceeds Expectations'),
        (4, 'Far Exceeds Expectations'),
    ]
    
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='performance_reviews'
    )
    
    review_date = models.DateField()
    review_period_start = models.DateField()
    review_period_end = models.DateField()
    
    # Ratings
    overall_rating = models.IntegerField(choices=RATING_CHOICES)
    quality_rating = models.IntegerField(choices=RATING_CHOICES)
    productivity_rating = models.IntegerField(choices=RATING_CHOICES)
    teamwork_rating = models.IntegerField(choices=RATING_CHOICES)
    leadership_rating = models.IntegerField(choices=RATING_CHOICES, blank=True, null=True)
    
    # Review Details
    strengths = models.TextField()
    areas_for_improvement = models.TextField()
    goals_for_next_period = models.TextField()
    
    # Reviewer
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='performance_reviews_given'
    )
    
    # Compensation Impact
    recommended_raise = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0,
        help_text="Recommended salary increase percentage"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-review_date']
        unique_together = ('employee', 'review_date')
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.review_date.strftime('%b %Y')}"


class Disciplinary(models.Model):
    """
    Track disciplinary actions and history.
    """
    ACTION_TYPES = [
        ('WARNING', 'Warning'),
        ('SUSPENSION', 'Suspension'),
        ('TERMINATION', 'Termination'),
        ('DEMOTION', 'Demotion'),
        ('OTHER', 'Other'),
    ]
    
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='disciplinary_actions'
    )
    
    action_type = models.CharField(max_length=50, choices=ACTION_TYPES)
    action_date = models.DateField()
    
    # Details
    reason = models.TextField()
    description = models.TextField()
    
    # Duration (if applicable)
    suspension_start = models.DateField(null=True, blank=True)
    suspension_end = models.DateField(null=True, blank=True)
    
    # Impact
    salary_deduction = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0,
        help_text="Any salary impact from disciplinary action"
    )
    
    # Reported By
    reported_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='disciplinary_reports'
    )
    
    is_resolved = models.BooleanField(default=False)
    resolved_date = models.DateField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-action_date']
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.get_action_type_display()} ({self.action_date})"


class SalaryHistory(models.Model):
    """
    Track salary changes and history for audit trail.
    """
    CHANGE_REASONS = [
        ('HIRE', 'New Hire'),
        ('PROMOTION', 'Promotion'),
        ('MERIT_INCREASE', 'Merit Increase'),
        ('PERFORMANCE_REVIEW', 'Performance Review'),
        ('ADJUSTMENT', 'Salary Adjustment'),
        ('COST_OF_LIVING', 'Cost of Living Adjustment'),
        ('RESTRUCTURE', 'Restructure'),
        ('TERMINATION', 'Termination'),
        ('OTHER', 'Other'),
    ]
    
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='salary_history'
    )
    
    effective_date = models.DateField(db_index=True)
    
    # Salary Info
    salary_before = models.DecimalField(max_digits=18, decimal_places=2)
    salary_after = models.DecimalField(max_digits=18, decimal_places=2)
    
    change_reason = models.CharField(max_length=50, choices=CHANGE_REASONS)
    
    # Details
    performance_rating = models.IntegerField(null=True, blank=True)
    approval_notes = models.TextField(blank=True)
    
    # Approvals
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='salary_approvals'
    )
    approved_date = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-effective_date']
        indexes = [
            models.Index(fields=['employee', 'effective_date']),
        ]
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.get_change_reason_display()} ({self.effective_date})"


class Attendance(models.Model):
    """
    Track daily attendance.
    """
    STATUS_CHOICES = [
        ('PRESENT', 'Present'),
        ('ABSENT', 'Absent'),
        ('LATE', 'Late'),
        ('LEAVE', 'Leave'),
        ('HOLIDAY', 'Holiday'),
    ]
    
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='attendance'
    )
    attendance_date = models.DateField(db_index=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    
    # Time Tracking
    check_in_time = models.TimeField(null=True, blank=True)
    check_out_time = models.TimeField(null=True, blank=True)
    hours_worked = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0
    )
    
    # Notes
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('employee', 'attendance_date')
        ordering = ['-attendance_date']
        indexes = [
            models.Index(fields=['employee', 'attendance_date']),
        ]
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.attendance_date} ({self.status})"
