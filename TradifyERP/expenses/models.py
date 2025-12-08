"""
Employee Expense Tracking Module Models
Handles employee expenses, approvals, and reimbursement
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
from django.core.validators import MinValueValidator
from accounting.models import Entity, Account, LedgerEntry, AuditLog
from hr.models import Employee
import os


class ExpenseCategory(models.Model):
    """Expense categories/types (Travel, Meals, Office Supplies, etc.)"""
    
    CATEGORY_TYPES = [
        ('TRAVEL', 'Travel'),
        ('MEALS', 'Meals & Entertainment'),
        ('OFFICE_SUPPLIES', 'Office Supplies'),
        ('ACCOMMODATION', 'Accommodation'),
        ('TRANSPORTATION', 'Transportation'),
        ('UTILITIES', 'Utilities'),
        ('MAINTENANCE', 'Maintenance'),
        ('EQUIPMENT', 'Equipment'),
        ('PROFESSIONAL_SERVICES', 'Professional Services'),
        ('TRAINING', 'Training & Development'),
        ('COMMUNICATIONS', 'Communications'),
        ('OTHER', 'Other'),
    ]
    
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE, related_name='expense_categories')
    category_type = models.CharField(max_length=50, choices=CATEGORY_TYPES)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    # GL Account for posting approved expenses
    expense_account = models.ForeignKey(
        Account,
        on_delete=models.SET_NULL,
        null=True,
        related_name='expense_categories',
        help_text="GL account to post approved expenses"
    )
    
    # Expense Limits
    daily_limit = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text="Daily spending limit for this category (per employee)"
    )
    monthly_limit = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text="Monthly spending limit for this category (per employee)"
    )
    
    requires_receipt = models.BooleanField(default=True, help_text="Receipt required for this category")
    requires_approval = models.BooleanField(default=True, help_text="Manager approval required")
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        unique_together = ('entity', 'category_type')
    
    def __str__(self):
        return f"{self.name} ({self.get_category_type_display()})"


class EmployeeExpenseReport(models.Model):
    """Employee expense report - contains multiple expense items"""
    
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('SUBMITTED', 'Submitted'),
        ('PENDING_REVIEW', 'Pending Review'),
        ('PENDING_APPROVAL', 'Pending Approval'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('REIMBURSED', 'Reimbursed'),
        ('POSTED', 'Posted to GL'),
    ]
    
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE, related_name='expense_reports')
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='expense_reports')
    
    # Report Details
    report_date = models.DateField(auto_now_add=True)
    period_start = models.DateField(help_text="Period start date for expenses")
    period_end = models.DateField(help_text="Period end date for expenses")
    description = models.TextField(blank=True, help_text="Additional notes about the report")
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    
    # Submission Info
    submitted_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='submitted_expense_reports'
    )
    submitted_at = models.DateTimeField(null=True, blank=True)
    
    # Review Info
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_expense_reports'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_notes = models.TextField(blank=True)
    
    # Approval Info
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_expense_reports'
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    approval_notes = models.TextField(blank=True)
    
    # Rejection Info
    rejection_reason = models.TextField(blank=True)
    rejected_at = models.DateTimeField(null=True, blank=True)
    
    # Reimbursement Info
    reimbursement_date = models.DateField(null=True, blank=True)
    reimbursement_method = models.CharField(
        max_length=50,
        choices=[
            ('BANK_TRANSFER', 'Bank Transfer'),
            ('CHECK', 'Check'),
            ('CASH', 'Cash'),
            ('PAYROLL', 'Payroll Deduction'),
        ],
        blank=True
    )
    
    # GL Posting
    is_posted = models.BooleanField(default=False)
    posted_at = models.DateTimeField(null=True, blank=True)
    
    # Totals (calculated)
    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text="Total expense amount"
    )
    total_approved = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text="Total approved amount"
    )
    total_rejected = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text="Total rejected amount"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-period_end']
        verbose_name_plural = "Employee Expense Reports"
        permissions = [
            ("review_employeeexpensereport", "Can review employee expense reports"),
            ("approve_employeeexpensereport", "Can approve employee expense reports"),
        ]
    
    def __str__(self):
        return f"Expense Report - {self.employee.user.get_full_name()} ({self.period_start} to {self.period_end})"
    
    def calculate_totals(self):
        """Recalculate total amounts from expense items"""
        self.total_amount = sum(item.amount for item in self.items.all())
        self.total_approved = sum(
            item.amount for item in self.items.filter(status='APPROVED')
        )
        self.total_rejected = sum(
            item.amount for item in self.items.filter(status='REJECTED')
        )
        self.save()
    
    def submit(self, user):
        """Submit report for review"""
        self.status = 'SUBMITTED'
        self.submitted_by = user
        self.submitted_at = timezone.now()
        self.save()
        
        # Create audit log
        AuditLog.objects.create(
            entity=self.entity,
            action='SUBMIT',
            model_name='EmployeeExpenseReport',
            object_id=str(self.id),
            user=user.username,
            description=f"Submitted expense report: {self}",
            old_values={'status': 'DRAFT'},
            new_values={'status': 'SUBMITTED'}
        )
    
    def approve(self, user, notes=""):
        """Approve the report and post to GL"""
        self.status = 'APPROVED'
        self.approved_by = user
        self.approved_at = timezone.now()
        self.approval_notes = notes
        self.save()
        
        # Create audit log
        AuditLog.objects.create(
            entity=self.entity,
            action='APPROVE',
            model_name='EmployeeExpenseReport',
            object_id=str(self.id),
            user=user.username,
            description=f"Approved expense report: {self}",
            old_values={'status': 'PENDING_APPROVAL'},
            new_values={'status': 'APPROVED'}
        )
    
    def reject(self, user, reason=""):
        """Reject the report"""
        self.status = 'REJECTED'
        self.rejection_reason = reason
        self.rejected_at = timezone.now()
        self.save()
        
        # Create audit log
        AuditLog.objects.create(
            entity=self.entity,
            action='REJECT',
            model_name='EmployeeExpenseReport',
            object_id=str(self.id),
            user=user.username,
            description=f"Rejected expense report: {self}",
            old_values={'status': self.status},
            new_values={'status': 'REJECTED', 'reason': reason}
        )
    
    def post_to_gl(self):
        """Post approved expenses to general ledger"""
        if self.is_posted or self.status != 'APPROVED':
            return False
        
        try:
            for item in self.items.filter(status='APPROVED'):
                item.post_to_gl()
            
            self.is_posted = True
            self.posted_at = timezone.now()
            self.save()
            
            return True
        except Exception as e:
            print(f"Error posting to GL: {e}")
            return False


class EmployeeExpense(models.Model):
    """Individual expense item within a report"""
    
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('SUBMITTED', 'Submitted'),
        ('PENDING_APPROVAL', 'Pending Approval'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('POSTED', 'Posted to GL'),
    ]
    
    report = models.ForeignKey(
        EmployeeExpenseReport,
        on_delete=models.CASCADE,
        related_name='items'
    )
    category = models.ForeignKey(ExpenseCategory, on_delete=models.PROTECT)
    
    # Expense Details
    expense_date = models.DateField()
    description = models.TextField()
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    
    # Supporting Documentation
    receipt = models.FileField(
        upload_to='expense_receipts/%Y/%m/',
        null=True,
        blank=True,
        help_text="Receipt or supporting document"
    )
    receipt_number = models.CharField(max_length=100, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    
    # Approval Details
    approval_notes = models.TextField(blank=True)
    rejection_reason = models.TextField(blank=True)
    
    # GL Posting
    is_posted = models.BooleanField(default=False)
    posted_at = models.DateTimeField(null=True, blank=True)
    ledger_entry = models.ForeignKey(
        LedgerEntry,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='expense_items'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-expense_date']
    
    def __str__(self):
        return f"{self.category.name} - {self.amount} ({self.expense_date})"
    
    def approve(self):
        """Approve the expense item"""
        self.status = 'APPROVED'
        self.save()
    
    def reject(self, reason=""):
        """Reject the expense item"""
        self.status = 'REJECTED'
        self.rejection_reason = reason
        self.save()
    
    def post_to_gl(self):
        """Post approved expense to general ledger"""
        if self.is_posted or self.status != 'APPROVED':
            return False
        
        try:
            # Create debit entry for expense account
            ledger_entry = LedgerEntry.objects.create(
                account=self.category.expense_account,
                entity=self.report.entity,
                entry_date=self.expense_date,
                entry_type='DEBIT',
                amount=self.amount,
                description=f"Employee Expense - {self.description}",
                reference_number=f"EXP-{self.report.id}-{self.id}",
                is_posted=True
            )
            
            self.ledger_entry = ledger_entry
            self.is_posted = True
            self.posted_at = timezone.now()
            self.status = 'POSTED'
            self.save()
            
            return True
        except Exception as e:
            print(f"Error posting expense to GL: {e}")
            return False


class ExpenseAttachment(models.Model):
    """Attachments (receipts, bills, invoices) for expense reports or items"""
    
    ATTACHMENT_TYPES = [
        ('RECEIPT', 'Receipt'),
        ('INVOICE', 'Invoice'),
        ('BILL', 'Bill'),
        ('PROOF_OF_PAYMENT', 'Proof of Payment'),
        ('OTHER', 'Other Supporting Document'),
    ]
    
    # Attachments can be linked to either report or individual item
    report = models.ForeignKey(
        EmployeeExpenseReport,
        on_delete=models.CASCADE,
        related_name='attachments',
        null=True,
        blank=True
    )
    expense_item = models.ForeignKey(
        EmployeeExpense,
        on_delete=models.CASCADE,
        related_name='attachments',
        null=True,
        blank=True
    )
    
    # Attachment Details
    attachment_type = models.CharField(
        max_length=20,
        choices=ATTACHMENT_TYPES,
        default='RECEIPT'
    )
    file = models.FileField(
        upload_to='expense_attachments/%Y/%m/',
        help_text="Upload receipt, invoice, or supporting document"
    )
    file_name = models.CharField(max_length=255)
    file_size = models.BigIntegerField(default=0)
    file_type = models.CharField(max_length=100, blank=True)
    
    description = models.TextField(blank=True, help_text="Description of the attachment")
    
    # Metadata
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='uploaded_expense_attachments'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_attachment_type_display()} - {self.file_name}"
    
    def save(self, *args, **kwargs):
        if self.file:
            self.file_name = self.file.name
            self.file_size = self.file.size
            self.file_type = os.path.splitext(self.file.name)[1].lstrip('.')
        super().save(*args, **kwargs)
    
    def get_file_url(self):
        """Get the URL for the file"""
        if self.file:
            return self.file.url
        return None



class ExpenseBudget(models.Model):
    """Employee expense budgets by category"""
    
    PERIOD_CHOICES = [
        ('DAILY', 'Daily'),
        ('WEEKLY', 'Weekly'),
        ('MONTHLY', 'Monthly'),
        ('QUARTERLY', 'Quarterly'),
        ('ANNUAL', 'Annual'),
    ]
    
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE, related_name='expense_budgets')
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='expense_budgets')
    category = models.ForeignKey(ExpenseCategory, on_delete=models.CASCADE)
    
    period = models.CharField(max_length=20, choices=PERIOD_CHOICES, default='MONTHLY')
    budget_amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    
    # Period tracking
    period_start = models.DateField()
    period_end = models.DateField()
    
    # Tracking
    spent_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    approved_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-period_end']
        unique_together = ('employee', 'category', 'period_start')
    
    def __str__(self):
        return f"{self.employee.user.get_full_name()} - {self.category.name} ({self.period})"
    
    def get_remaining_budget(self):
        """Calculate remaining budget"""
        return max(Decimal('0'), self.budget_amount - self.spent_amount)
    
    def is_over_budget(self):
        """Check if over budget"""
        return self.spent_amount > self.budget_amount
    
    def get_variance_percent(self):
        """Get budget variance as percentage"""
        if self.budget_amount == 0:
            return 0
        return (self.spent_amount / self.budget_amount) * 100


class ExpenseApprovalWorkflow(models.Model):
    """Approval workflow for expense reports"""
    
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('PENDING_MANAGER_REVIEW', 'Pending Manager Review'),
        ('PENDING_FINANCE_APPROVAL', 'Pending Finance Approval'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]
    
    report = models.OneToOneField(
        EmployeeExpenseReport,
        on_delete=models.CASCADE,
        related_name='approval_workflow'
    )
    
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='DRAFT')
    
    # Manager Review
    manager = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_expense_workflows'
    )
    manager_review_at = models.DateTimeField(null=True, blank=True)
    manager_approved = models.BooleanField(default=False)
    manager_notes = models.TextField(blank=True)
    
    # Finance Approval
    finance_approver = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_expense_workflows'
    )
    finance_approved_at = models.DateTimeField(null=True, blank=True)
    finance_approved = models.BooleanField(default=False)
    finance_notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Approval Workflow - {self.report}"
    
    def submit_for_manager_review(self):
        """Submit to manager for review"""
        self.status = 'PENDING_MANAGER_REVIEW'
        self.save()
    
    def manager_approve(self, manager, notes=""):
        """Manager approves the report"""
        self.manager = manager
        self.manager_approved = True
        self.manager_review_at = timezone.now()
        self.manager_notes = notes
        self.status = 'PENDING_FINANCE_APPROVAL'
        self.save()
    
    def finance_approve(self, approver, notes=""):
        """Finance approves the report"""
        self.finance_approver = approver
        self.finance_approved = True
        self.finance_approved_at = timezone.now()
        self.finance_notes = notes
        self.status = 'APPROVED'
        self.save()
        
        # Update report status
        self.report.approve(approver, notes)


class ExpenseReimbursement(models.Model):
    """Track expense reimbursements to employees"""
    
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('SCHEDULED', 'Scheduled'),
        ('PROCESSING', 'Processing'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]
    
    report = models.OneToOneField(
        EmployeeExpenseReport,
        on_delete=models.CASCADE,
        related_name='reimbursement'
    )
    
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    
    # Payment Details
    method = models.CharField(
        max_length=50,
        choices=[
            ('BANK_TRANSFER', 'Bank Transfer'),
            ('CHECK', 'Check'),
            ('CASH', 'Cash'),
            ('PAYROLL', 'Payroll Deduction'),
        ],
        default='BANK_TRANSFER'
    )
    
    scheduled_date = models.DateField(null=True, blank=True)
    completion_date = models.DateField(null=True, blank=True)
    
    # Reference
    transaction_id = models.CharField(max_length=100, blank=True, unique=True)
    notes = models.TextField(blank=True)
    
    # GL Posting
    is_posted = models.BooleanField(default=False)
    posted_at = models.DateTimeField(null=True, blank=True)
    ledger_entries = models.ManyToManyField(LedgerEntry, blank=True, related_name='reimbursements')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Reimbursement - {self.report.employee.user.get_full_name()} ({self.amount})"
    
    def schedule_payment(self, scheduled_date):
        """Schedule reimbursement payment"""
        self.scheduled_date = scheduled_date
        self.status = 'SCHEDULED'
        self.save()
    
    def complete_payment(self, transaction_id=""):
        """Mark reimbursement as completed"""
        self.completion_date = timezone.now().date()
        self.status = 'COMPLETED'
        if transaction_id:
            self.transaction_id = transaction_id
        self.save()
    
    def mark_failed(self, notes=""):
        """Mark payment as failed"""
        self.status = 'FAILED'
        self.notes = notes
        self.save()
