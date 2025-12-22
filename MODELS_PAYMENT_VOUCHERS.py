"""
PAYMENT MODELS - Cash & Bank Payment Workflows
Models for Cash Payment Vouchers (CPV) and Bank Payment Vouchers (BPV)
Implements complete payment workflow: DRAFT → APPROVED → AUTHORIZED → GL_POSTED
"""

from django.db import models
from django.contrib.auth.models import User
from django.db.models import Index
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal


# ============================================================================
# CASH PAYMENT VOUCHER MODELS
# ============================================================================

class CashPaymentVoucher(models.Model):
    """
    Header model for Cash Payment Vouchers (CPV)
    Tracks payment from petty cash or cash account
    Workflow: DRAFT → SUBMITTED → CHECKED → AUTHORIZED → GL_POSTED
    """
    
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('SUBMITTED_FOR_APPROVAL', 'Submitted for Approval'),
        ('CHECKED', 'Checked'),
        ('REJECTED', 'Rejected'),
        ('AUTHORIZED', 'Authorized'),
        ('GL_POSTED', 'GL Posted'),
        ('REVERSED', 'Reversed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    # Identifiers
    voucher_number = models.CharField(
        max_length=50, 
        unique=True,
        help_text="Auto-generated: CPV/YYYY/NNNN"
    )
    voucher_date = models.DateField(
        default=timezone.now,
        help_text="Date of payment request"
    )
    entity = models.ForeignKey(
        'Entity',
        on_delete=models.PROTECT,
        related_name='cash_payment_vouchers'
    )
    
    # Payee Information
    payee_name = models.CharField(
        max_length=255,
        help_text="Name of person/entity receiving cash"
    )
    payee_id = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Link to Stakeholder if employee"
    )
    
    # Amounts
    total_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="Total payment amount"
    )
    
    # Metadata
    description = models.TextField(
        blank=True,
        help_text="Payment purpose/narration"
    )
    reference_document = models.CharField(
        max_length=255,
        blank=True,
        help_text="Reference invoice/receipt number"
    )
    
    # Workflow Status
    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default='DRAFT'
    )
    
    # Approvals
    maker = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='cash_payments_made_by',
        null=True,
        help_text="User who created the voucher"
    )
    maker_date = models.DateTimeField(
        auto_now_add=True,
        help_text="When voucher was created"
    )
    
    checker = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='cash_payments_checked_by',
        null=True,
        blank=True,
        help_text="User who checked the voucher"
    )
    checker_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When voucher was checked"
    )
    checker_comments = models.TextField(
        blank=True,
        help_text="Checker's remarks"
    )
    
    approver = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='cash_payments_approved_by',
        null=True,
        blank=True,
        help_text="User who authorized the payment"
    )
    approver_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When payment was authorized"
    )
    approver_comments = models.TextField(
        blank=True,
        help_text="Approver's remarks"
    )
    
    # GL Posting
    journal_entry = models.ForeignKey(
        'accounting.JournalEntry',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cash_payment_vouchers',
        help_text="Associated GL entry"
    )
    gl_posting_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When GL entries were posted"
    )
    
    # Audit
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='cash_payment_vouchers_created'
    )
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-voucher_date', '-id']
        verbose_name = 'Cash Payment Voucher'
        verbose_name_plural = 'Cash Payment Vouchers'
        permissions = [
            ('can_approve_cash_payment', 'Can approve cash payments'),
            ('can_authorize_cash_payment', 'Can authorize cash payments'),
            ('can_reverse_cash_payment', 'Can reverse cash payments'),
        ]
        indexes = [
            Index(fields=['entity', 'voucher_date']),
            Index(fields=['status']),
            Index(fields=['voucher_number']),
            Index(fields=['maker', 'status']),
            Index(fields=['checker', 'status']),
            Index(fields=['approver', 'status']),
        ]
    
    def __str__(self):
        return f"{self.voucher_number} - {self.payee_name} - {self.total_amount}"
    
    def get_line_items_total(self):
        """Calculate total from line items"""
        return self.lines.aggregate(
            total=models.Sum('amount')
        )['total'] or Decimal('0.00')
    
    def is_balanced(self):
        """Check if lines total equals header total"""
        return self.get_line_items_total() == self.total_amount
    
    def can_submit(self):
        """Check if voucher can be submitted for approval"""
        return self.status == 'DRAFT' and self.is_balanced() and self.lines.exists()
    
    def can_approve(self):
        """Check if voucher can be approved"""
        return self.status == 'SUBMITTED_FOR_APPROVAL'
    
    def can_authorize(self):
        """Check if voucher can be authorized"""
        return self.status == 'CHECKED'
    
    def can_reverse(self):
        """Check if voucher can be reversed"""
        return self.status == 'GL_POSTED'


class CashPaymentLine(models.Model):
    """
    Line item model for Cash Payment Vouchers
    Each line represents a separate expense/payment component
    """
    
    # Relationships
    voucher = models.ForeignKey(
        CashPaymentVoucher,
        on_delete=models.CASCADE,
        related_name='lines'
    )
    
    # Line Details
    line_number = models.PositiveIntegerField(
        help_text="Sequential line number"
    )
    description = models.CharField(
        max_length=500,
        help_text="Description of payment/expense"
    )
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="Amount for this line item"
    )
    
    # GL Accounts
    expense_account = models.ForeignKey(
        'accounting.GLAccount',
        on_delete=models.PROTECT,
        related_name='cash_payment_lines',
        help_text="Expense account to debit"
    )
    
    # Supporting Documents
    supporting_document = models.FileField(
        upload_to='payments/cash/%Y/%m/',
        null=True,
        blank=True,
        help_text="Invoice, receipt, or supporting doc"
    )
    document_reference = models.CharField(
        max_length=255,
        blank=True,
        help_text="Reference number from document"
    )
    
    # Tax (if applicable)
    tax_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Tax component of amount"
    )
    tax_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Tax percentage"
    )
    
    # GL Entry Link
    gl_entry = models.ForeignKey(
        'accounting.GLEntry',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cash_payment_lines',
        help_text="Posted GL entry"
    )
    
    # Audit
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['voucher', 'line_number']
        unique_together = [['voucher', 'line_number']]
        verbose_name = 'Cash Payment Line'
        verbose_name_plural = 'Cash Payment Lines'
    
    def __str__(self):
        return f"{self.voucher.voucher_number} - Line {self.line_number} - {self.amount}"


# ============================================================================
# BANK PAYMENT VOUCHER MODELS
# ============================================================================

class BankPaymentVoucher(models.Model):
    """
    Header model for Bank Payment Vouchers (BPV)
    Tracks payment via bank transfer, cheque, or DD
    Workflow: DRAFT → SUBMITTED → CHECKED → AUTHORIZED → GL_POSTED → CLEARED
    """
    
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('SUBMITTED_FOR_APPROVAL', 'Submitted for Approval'),
        ('CHECKED', 'Checked'),
        ('REJECTED', 'Rejected'),
        ('AUTHORIZED', 'Authorized'),
        ('GL_POSTED', 'GL Posted'),
        ('IN_TRANSIT', 'In Transit'),
        ('CLEARED', 'Cleared'),
        ('FAILED', 'Failed'),
        ('REVERSED', 'Reversed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    PAYMENT_MODE_CHOICES = [
        ('BANK_TRANSFER', 'Bank Transfer'),
        ('CHEQUE', 'Cheque'),
        ('DD', 'Demand Draft'),
    ]
    
    # Identifiers
    voucher_number = models.CharField(
        max_length=50,
        unique=True,
        help_text="Auto-generated: BPV/YYYY/NNNN"
    )
    voucher_date = models.DateField(
        default=timezone.now,
        help_text="Date of payment request"
    )
    entity = models.ForeignKey(
        'Entity',
        on_delete=models.PROTECT,
        related_name='bank_payment_vouchers'
    )
    
    # Payee Information
    payee_name = models.CharField(
        max_length=255,
        help_text="Vendor/supplier/recipient name"
    )
    payee_id = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Link to Stakeholder if vendor"
    )
    
    # Bank Details
    bank_account = models.ForeignKey(
        'accounting.BankAccount',
        on_delete=models.PROTECT,
        related_name='bank_payments_from'
    )
    beneficiary_account_number = models.CharField(
        max_length=50,
        help_text="Recipient's bank account number"
    )
    beneficiary_ifsc = models.CharField(
        max_length=20,
        help_text="IFSC code of recipient bank"
    )
    beneficiary_bank = models.CharField(
        max_length=255,
        help_text="Name of recipient's bank"
    )
    
    # Amounts
    total_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="Total payment amount"
    )
    
    # Metadata
    description = models.TextField(
        blank=True,
        help_text="Payment purpose/narration"
    )
    payment_mode = models.CharField(
        max_length=20,
        choices=PAYMENT_MODE_CHOICES,
        default='BANK_TRANSFER'
    )
    cheque_number = models.CharField(
        max_length=20,
        blank=True,
        help_text="Cheque number if payment mode is cheque"
    )
    
    # Workflow Status
    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default='DRAFT'
    )
    
    # Approvals
    maker = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='bank_payments_made_by',
        null=True,
        help_text="User who created the voucher"
    )
    maker_date = models.DateTimeField(
        auto_now_add=True,
        help_text="When voucher was created"
    )
    
    checker = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='bank_payments_checked_by',
        null=True,
        blank=True,
        help_text="User who checked the voucher"
    )
    checker_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When voucher was checked"
    )
    checker_comments = models.TextField(
        blank=True,
        help_text="Checker's remarks"
    )
    
    approver = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='bank_payments_approved_by',
        null=True,
        blank=True,
        help_text="User who authorized the payment"
    )
    approver_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When payment was authorized"
    )
    approver_comments = models.TextField(
        blank=True,
        help_text="Approver's remarks"
    )
    
    # GL Posting
    journal_entry = models.ForeignKey(
        'accounting.JournalEntry',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bank_payment_vouchers',
        help_text="Associated GL entry"
    )
    gl_posting_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When GL entries were posted"
    )
    
    # Bank Integration
    bank_reference = models.CharField(
        max_length=100,
        blank=True,
        help_text="Bank transaction reference number"
    )
    bank_status = models.CharField(
        max_length=50,
        blank=True,
        help_text="Bank transfer status"
    )
    bank_clearing_date = models.DateField(
        null=True,
        blank=True,
        help_text="When payment cleared in bank account"
    )
    
    # Audit
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='bank_payment_vouchers_created'
    )
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-voucher_date', '-id']
        verbose_name = 'Bank Payment Voucher'
        verbose_name_plural = 'Bank Payment Vouchers'
        permissions = [
            ('can_approve_bank_payment', 'Can approve bank payments'),
            ('can_authorize_bank_payment', 'Can authorize bank payments'),
            ('can_reverse_bank_payment', 'Can reverse bank payments'),
        ]
        indexes = [
            Index(fields=['entity', 'voucher_date']),
            Index(fields=['status']),
            Index(fields=['voucher_number']),
            Index(fields=['maker', 'status']),
            Index(fields=['checker', 'status']),
            Index(fields=['approver', 'status']),
        ]
    
    def __str__(self):
        return f"{self.voucher_number} - {self.payee_name} - {self.total_amount}"
    
    def get_line_items_total(self):
        """Calculate total from line items"""
        return self.lines.aggregate(
            total=models.Sum('amount')
        )['total'] or Decimal('0.00')
    
    def is_balanced(self):
        """Check if lines total equals header total"""
        return self.get_line_items_total() == self.total_amount
    
    def can_submit(self):
        """Check if voucher can be submitted for approval"""
        return self.status == 'DRAFT' and self.is_balanced() and self.lines.exists()
    
    def can_approve(self):
        """Check if voucher can be approved"""
        return self.status == 'SUBMITTED_FOR_APPROVAL'
    
    def can_authorize(self):
        """Check if voucher can be authorized"""
        return self.status == 'CHECKED'
    
    def can_reverse(self):
        """Check if voucher can be reversed"""
        return self.status == 'GL_POSTED'


class BankPaymentLine(models.Model):
    """
    Line item model for Bank Payment Vouchers
    Each line represents a separate payment/invoice
    """
    
    # Relationships
    voucher = models.ForeignKey(
        BankPaymentVoucher,
        on_delete=models.CASCADE,
        related_name='lines'
    )
    
    # Line Details
    line_number = models.PositiveIntegerField(
        help_text="Sequential line number"
    )
    description = models.CharField(
        max_length=500,
        help_text="Description of payment/invoice"
    )
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="Amount for this line item"
    )
    
    # GL Accounts (can be either payable or expense)
    payable_account = models.ForeignKey(
        'accounting.GLAccount',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='bank_payment_payable_lines',
        help_text="Payable account to debit (if settling invoice)"
    )
    expense_account = models.ForeignKey(
        'accounting.GLAccount',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='bank_payment_expense_lines',
        help_text="Expense account to debit (if direct expense)"
    )
    
    # References
    po_reference = models.CharField(
        max_length=50,
        blank=True,
        help_text="Purchase order number"
    )
    invoice_reference = models.CharField(
        max_length=50,
        blank=True,
        help_text="Vendor invoice number"
    )
    
    # Supporting Documents
    supporting_document = models.FileField(
        upload_to='payments/bank/%Y/%m/',
        null=True,
        blank=True,
        help_text="Invoice or supporting document"
    )
    document_reference = models.CharField(
        max_length=255,
        blank=True,
        help_text="Reference from document"
    )
    
    # Tax
    tax_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Tax component of amount"
    )
    tax_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Tax percentage"
    )
    net_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="Net amount (before tax)"
    )
    
    # GL Entry Link
    gl_entry = models.ForeignKey(
        'accounting.GLEntry',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bank_payment_lines',
        help_text="Posted GL entry"
    )
    
    # Audit
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['voucher', 'line_number']
        unique_together = [['voucher', 'line_number']]
        verbose_name = 'Bank Payment Line'
        verbose_name_plural = 'Bank Payment Lines'
    
    def __str__(self):
        return f"{self.voucher.voucher_number} - Line {self.line_number} - {self.amount}"
    
    def save(self, *args, **kwargs):
        """Ensure either payable or expense account is set"""
        if not self.payable_account and not self.expense_account:
            raise ValidationError("Either payable_account or expense_account must be specified")
        super().save(*args, **kwargs)
