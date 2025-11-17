"""
HR Module Enhancements - Brings HR Module from 9/10 to 9.5/10
Advanced features for compliance, security, and analytics
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal
import uuid


class EmployeeEncryption(models.Model):
    """
    Sensitive employee data encryption model.
    Stores encrypted SSN, bank account, and salary information.
    """
    employee = models.OneToOneField(
        'Employee',
        on_delete=models.CASCADE,
        related_name='encryption_data'
    )
    
    # Encrypted fields (use django-fernet or similar)
    ssn_encrypted = models.BinaryField(null=True, blank=True)
    bank_account_encrypted = models.BinaryField(null=True, blank=True)
    bank_routing_encrypted = models.BinaryField(null=True, blank=True)
    
    # Encryption metadata
    last_rotated = models.DateTimeField(auto_now=True)
    encryption_key_version = models.IntegerField(default=1)
    
    class Meta:
        verbose_name = "Employee Data Encryption"
        verbose_name_plural = "Employee Data Encryption"
    
    def __str__(self):
        return f"Encryption Data for {self.employee}"


class EmployeeComplianceStatus(models.Model):
    """
    Track employee compliance with policies and regulations.
    GDPR, SOX, local labor laws.
    """
    COMPLIANCE_STATUS = [
        ('COMPLIANT', 'Compliant'),
        ('NON_COMPLIANT', 'Non-Compliant'),
        ('PENDING_REVIEW', 'Pending Review'),
        ('EXEMPTED', 'Exempted'),
    ]
    
    COMPLIANCE_TYPES = [
        ('BACKGROUND_CHECK', 'Background Check'),
        ('TAX_FORM_W4', 'W-4 Form'),
        ('I9_VERIFICATION', 'I-9 Verification'),
        ('CONFIDENTIALITY_AGREEMENT', 'Confidentiality Agreement'),
        ('NON_COMPETE', 'Non-Compete Agreement'),
        ('HANDBOOK_ACKNOWLEDGMENT', 'Employee Handbook Acknowledgment'),
        ('GDPR_CONSENT', 'GDPR Data Consent'),
        ('DIRECT_DEPOSIT', 'Direct Deposit Setup'),
        ('EMERGENCY_CONTACT', 'Emergency Contact Information'),
        ('BENEFITS_ELECTION', 'Benefits Election'),
    ]
    
    employee = models.ForeignKey(
        'Employee',
        on_delete=models.CASCADE,
        related_name='compliance_status'
    )
    
    compliance_type = models.CharField(max_length=50, choices=COMPLIANCE_TYPES)
    status = models.CharField(max_length=20, choices=COMPLIANCE_STATUS, default='PENDING_REVIEW')
    
    # Evidence
    document_url = models.URLField(blank=True, null=True)
    completion_date = models.DateField(null=True, blank=True)
    expiration_date = models.DateField(null=True, blank=True)
    
    # Review
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    reviewed_date = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('employee', 'compliance_type')
        ordering = ['employee', 'compliance_type']
    
    def __str__(self):
        return f"{self.employee} - {self.get_compliance_type_display()}: {self.status}"


class EmployeeTraining(models.Model):
    """
    Track mandatory and optional employee training.
    Compliance training, safety, professional development.
    """
    TRAINING_STATUS = [
        ('SCHEDULED', 'Scheduled'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('EXEMPTED', 'Exempted'),
    ]
    
    TRAINING_TYPES = [
        ('MANDATORY', 'Mandatory'),
        ('COMPLIANCE', 'Compliance'),
        ('SAFETY', 'Safety'),
        ('PROFESSIONAL', 'Professional Development'),
        ('ONBOARDING', 'Onboarding'),
        ('OTHER', 'Other'),
    ]
    
    employee = models.ForeignKey(
        'Employee',
        on_delete=models.CASCADE,
        related_name='training_records'
    )
    
    training_type = models.CharField(max_length=50, choices=TRAINING_TYPES)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    # Dates
    scheduled_date = models.DateField()
    completion_date = models.DateField(null=True, blank=True)
    expiration_date = models.DateField(null=True, blank=True)
    
    # Status & Results
    status = models.CharField(max_length=20, choices=TRAINING_STATUS, default='SCHEDULED')
    score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    certificate_url = models.URLField(blank=True, null=True)
    
    # Tracking
    provider = models.CharField(max_length=255, blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['employee', '-scheduled_date']
    
    def __str__(self):
        return f"{self.employee} - {self.title}"


class EmployeeExitProcess(models.Model):
    """
    Track employee separation process.
    Offboarding, final paycheck, benefits COBRA, etc.
    """
    EXIT_TYPES = [
        ('RESIGNATION', 'Resignation'),
        ('TERMINATION', 'Termination'),
        ('RETIREMENT', 'Retirement'),
        ('LAYOFF', 'Layoff'),
    ]
    
    EXIT_STATUS = [
        ('NOTICE_GIVEN', 'Notice Given'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('RETURNED_TO_WORK', 'Returned to Work'),
    ]
    
    employee = models.OneToOneField(
        'Employee',
        on_delete=models.CASCADE,
        related_name='exit_process'
    )
    
    exit_type = models.CharField(max_length=20, choices=EXIT_TYPES)
    exit_date = models.DateField()
    notice_date = models.DateField()
    status = models.CharField(max_length=20, choices=EXIT_STATUS, default='NOTICE_GIVEN')
    
    # Details
    reason = models.TextField()
    final_paycheck_issued = models.BooleanField(default=False)
    final_paycheck_date = models.DateField(null=True, blank=True)
    accrued_paid_time_off_paid = models.BooleanField(default=False)
    
    # COBRA & Benefits
    cobra_offered = models.BooleanField(default=False)
    health_insurance_end_date = models.DateField(null=True, blank=True)
    
    # Equipment Return
    equipment_returned = models.BooleanField(default=False)
    equipment_details = models.TextField(blank=True)
    
    # Access Revocation
    access_revoked = models.BooleanField(default=False)
    access_revocation_date = models.DateField(null=True, blank=True)
    
    # References
    eligibility_for_rehire = models.CharField(
        max_length=20,
        choices=[('YES', 'Yes'), ('NO', 'No'), ('CONDITIONAL', 'Conditional')],
        default='YES'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Employee Exit Process"
        verbose_name_plural = "Employee Exit Processes"
    
    def __str__(self):
        return f"Exit Process - {self.employee} ({self.exit_date})"


class PayrollAudit(models.Model):
    """
    Comprehensive payroll audit trail.
    Tracks all changes to payroll for compliance & dispute resolution.
    """
    ACTION_TYPES = [
        ('CREATED', 'Created'),
        ('MODIFIED', 'Modified'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('POSTED_TO_GL', 'Posted to GL'),
        ('CORRECTED', 'Corrected'),
        ('VOIDED', 'Voided'),
    ]
    
    payroll = models.ForeignKey(
        'Payroll',
        on_delete=models.CASCADE,
        related_name='audit_trail'
    )
    
    action = models.CharField(max_length=20, choices=ACTION_TYPES)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    # Before/After
    changes = models.JSONField(default=dict, help_text="JSON diff of changes")
    previous_status = models.CharField(max_length=50, blank=True)
    new_status = models.CharField(max_length=50, blank=True)
    
    # Notes
    notes = models.TextField(blank=True)
    approval_reason = models.TextField(blank=True)
    
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Payroll Audit"
        verbose_name_plural = "Payroll Audits"
    
    def __str__(self):
        return f"Payroll {self.payroll} - {self.action} by {self.user}"


class PayrollDeduction(models.Model):
    """
    Detailed payroll deduction tracking.
    Tax, insurance, garnishments, etc.
    """
    DEDUCTION_TYPES = [
        ('FEDERAL_INCOME_TAX', 'Federal Income Tax'),
        ('STATE_INCOME_TAX', 'State Income Tax'),
        ('FICA', 'FICA (Social Security & Medicare)'),
        ('LOCAL_TAX', 'Local Tax'),
        ('HEALTH_INSURANCE', 'Health Insurance'),
        ('DENTAL_INSURANCE', 'Dental Insurance'),
        ('VISION_INSURANCE', 'Vision Insurance'),
        ('401K', '401(k) Contribution'),
        ('LIFE_INSURANCE', 'Life Insurance'),
        ('GARNISHMENT', 'Wage Garnishment'),
        ('CHILD_SUPPORT', 'Child Support'),
        ('LOAN_REPAYMENT', 'Loan Repayment'),
        ('OTHER', 'Other'),
    ]
    
    payroll_record = models.ForeignKey(
        'PayrollRecord',
        on_delete=models.CASCADE,
        related_name='deductions'
    )
    
    deduction_type = models.CharField(max_length=50, choices=DEDUCTION_TYPES)
    description = models.CharField(max_length=255, blank=True)
    
    # Amount
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    
    # GL Account
    expense_account = models.ForeignKey(
        'accounting.Account',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payroll_deductions'
    )
    
    # Compliance
    is_pretax = models.BooleanField(default=False)
    is_required = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['payroll_record', 'deduction_type']
    
    def __str__(self):
        return f"{self.get_deduction_type_display()}: ${self.amount}"


class EmployeeEarning(models.Model):
    """
    Detailed payroll earnings tracking.
    Regular pay, overtime, bonuses, etc.
    """
    EARNING_TYPES = [
        ('REGULAR', 'Regular Pay'),
        ('OVERTIME', 'Overtime (1.5x)'),
        ('DOUBLE_TIME', 'Double Time'),
        ('BONUS', 'Bonus'),
        ('COMMISSION', 'Commission'),
        ('HOLIDAY_PAY', 'Holiday Pay'),
        ('SICK_PAY', 'Sick Pay'),
        ('VACATION_PAY', 'Vacation Pay'),
        ('OTHER', 'Other'),
    ]
    
    payroll_record = models.ForeignKey(
        'PayrollRecord',
        on_delete=models.CASCADE,
        related_name='earnings'
    )
    
    earning_type = models.CharField(max_length=50, choices=EARNING_TYPES)
    description = models.CharField(max_length=255, blank=True)
    
    # Calculation
    quantity = models.DecimalField(max_digits=8, decimal_places=2)  # Hours for hourly, units for piecework
    rate = models.DecimalField(max_digits=12, decimal_places=2)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    
    # GL Account
    expense_account = models.ForeignKey(
        'accounting.Account',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payroll_earnings'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['payroll_record', 'earning_type']
    
    def __str__(self):
        return f"{self.get_earning_type_display()}: ${self.amount}"


class EmployeeWorkHistory(models.Model):
    """
    Track employee role changes and career progression.
    """
    employee = models.ForeignKey(
        'Employee',
        on_delete=models.CASCADE,
        related_name='work_history'
    )
    
    # Role
    position = models.ForeignKey(
        'Position',
        on_delete=models.SET_NULL,
        null=True
    )
    department = models.ForeignKey(
        'Department',
        on_delete=models.SET_NULL,
        null=True
    )
    
    # Dates
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    
    # Details
    reason_for_change = models.CharField(max_length=255, blank=True)
    salary_before = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    salary_after = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    # Reporting
    reporting_manager = models.ForeignKey(
        'Employee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='supervised_employees'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['employee', '-start_date']
    
    def __str__(self):
        return f"{self.employee} - {self.position} ({self.start_date})"
