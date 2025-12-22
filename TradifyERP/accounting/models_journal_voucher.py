"""
Journal Voucher Model for TradifyERP
Handles all manual accounting entries including:
- Sales returns
- Purchase returns  
- Shareholder transactions
- Employee payments
- All payments and receipts
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from decimal import Decimal


class JournalVoucher(models.Model):
    """
    Journal Voucher - Master document for all manual GL entries
    """
    VOUCHER_TYPE_CHOICES = [
        ('SALES_RETURN', 'Sales Return'),
        ('PURCHASE_RETURN', 'Purchase Return'),
        ('PAYMENT', 'Payment'),
        ('RECEIPT', 'Receipt'),
        ('SHAREHOLDER', 'Shareholder Transaction'),
        ('EMPLOYEE', 'Employee Transaction'),
        ('GENERAL', 'General Journal Entry'),
        ('ADJUSTMENT', 'Adjustment Entry'),
    ]
    
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('PENDING_APPROVAL', 'Pending Approval'),
        ('APPROVED', 'Approved'),
        ('POSTED', 'Posted'),
        ('REJECTED', 'Rejected'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    # Header Information
    voucher_number = models.CharField(max_length=50, unique=True, db_index=True)
    voucher_date = models.DateField()
    voucher_type = models.CharField(max_length=20, choices=VOUCHER_TYPE_CHOICES)
    entity = models.ForeignKey('Entity', on_delete=models.PROTECT, related_name='journal_vouchers')
    
    # Reference Information
    reference_number = models.CharField(max_length=100, blank=True, null=True, help_text="External reference number")
    reference_type = models.CharField(max_length=50, blank=True, null=True, help_text="Type of referenced document")
    description = models.TextField(help_text="Voucher description/narration")
    
    # Workflow
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    is_posted = models.BooleanField(default=False)
    posted_date = models.DateTimeField(blank=True, null=True)
    posted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='posted_vouchers')
    
    # Approval Workflow
    prepared_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='prepared_vouchers')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_vouchers')
    approved_date = models.DateTimeField(blank=True, null=True)
    
    # Audit Fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_vouchers')
    
    # Additional Info
    attachment = models.FileField(upload_to='journal_vouchers/', blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'journal_voucher'
        ordering = ['-voucher_date', '-voucher_number']
        verbose_name = 'Journal Voucher'
        verbose_name_plural = 'Journal Vouchers'
        indexes = [
            models.Index(fields=['voucher_date', 'entity']),
            models.Index(fields=['status']),
            models.Index(fields=['voucher_type']),
        ]
    
    def __str__(self):
        return f"{self.voucher_number} - {self.get_voucher_type_display()} ({self.voucher_date})"
    
    def clean(self):
        """Validate voucher before saving"""
        super().clean()
        
        # Check if voucher is balanced
        if self.pk:  # Only check if voucher exists
            if not self.is_balanced():
                raise ValidationError("Journal voucher must be balanced (Total Debits = Total Credits)")
    
    def is_balanced(self):
        """Check if total debits equal total credits"""
        total_debit = self.lines.filter(entry_type='DEBIT').aggregate(
            total=models.Sum('amount'))['total'] or Decimal('0')
        total_credit = self.lines.filter(entry_type='CREDIT').aggregate(
            total=models.Sum('amount'))['total'] or Decimal('0')
        return total_debit == total_credit
    
    def get_total_debit(self):
        """Get total debit amount"""
        return self.lines.filter(entry_type='DEBIT').aggregate(
            total=models.Sum('amount'))['total'] or Decimal('0')
    
    def get_total_credit(self):
        """Get total credit amount"""
        return self.lines.filter(entry_type='CREDIT').aggregate(
            total=models.Sum('amount'))['total'] or Decimal('0')
    
    def post(self, user=None):
        """Post journal voucher to ledger"""
        from django.utils import timezone
        
        if self.is_posted:
            raise ValidationError("Voucher is already posted")
        
        if not self.is_balanced():
            raise ValidationError("Cannot post unbalanced voucher")
        
        # Create ledger entries for each line
        for line in self.lines.all():
            LedgerEntry.objects.create(
                account=line.account,
                entity=self.entity,
                entry_date=self.voucher_date,
                entry_type=line.entry_type,
                amount=line.amount,
                description=f"{self.description} - {line.description}" if line.description else self.description,
                reference_number=self.voucher_number,
                is_posted=True,
                workflow_status='APPROVED'
            )
        
        # Mark as posted
        self.is_posted = True
        self.status = 'POSTED'
        self.posted_date = timezone.now()
        self.posted_by = user
        self.save()


class JournalVoucherLine(models.Model):
    """
    Journal Voucher Lines - Individual debit/credit entries
    """
    ENTRY_TYPE_CHOICES = [
        ('DEBIT', 'Debit'),
        ('CREDIT', 'Credit'),
    ]
    
    voucher = models.ForeignKey(JournalVoucher, on_delete=models.CASCADE, related_name='lines')
    line_number = models.IntegerField(help_text="Line sequence number")
    account = models.ForeignKey('Account', on_delete=models.PROTECT, related_name='journal_lines')
    entry_type = models.CharField(max_length=10, choices=ENTRY_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    description = models.TextField(blank=True, null=True, help_text="Line item description")
    
    # Optional linking fields
    stakeholder = models.ForeignKey('Stakeholder', on_delete=models.SET_NULL, null=True, blank=True, 
                                   help_text="Link to shareholder if applicable")
    employee = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='employee_journal_lines', help_text="Link to employee if applicable")
    
    # Dimensions for reporting
    cost_center = models.CharField(max_length=100, blank=True, null=True)
    project = models.CharField(max_length=100, blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'journal_voucher_line'
        ordering = ['line_number']
        verbose_name = 'Journal Voucher Line'
        verbose_name_plural = 'Journal Voucher Lines'
        unique_together = ('voucher', 'line_number')
    
    def __str__(self):
        return f"{self.voucher.voucher_number} - Line {self.line_number}: {self.account.name} ({self.entry_type}) ₹{self.amount}"
    
    def clean(self):
        """Validate line item"""
        super().clean()
        
        if self.amount <= 0:
            raise ValidationError("Amount must be greater than zero")


# Import statement for LedgerEntry (assuming it exists in accounting.models)
from .models import LedgerEntry, Entity, Account, Stakeholder
