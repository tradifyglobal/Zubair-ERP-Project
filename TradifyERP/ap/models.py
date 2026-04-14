from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal
from django.utils import timezone
from accounting.models import Entity, Account, LedgerEntry, Vendor


class VendorBill(models.Model):
    """Vendor bill/invoice record - represents what vendor bills us"""
    
    BILL_STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('RECEIVED', 'Received'),
        ('APPROVED', 'Approved'),
        ('PARTIAL', 'Partially Paid'),
        ('PAID', 'Fully Paid'),
        ('CANCELLED', 'Cancelled'),
        ('OVERDUE', 'Overdue'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('UNPAID', 'Unpaid'),
        ('PARTIAL', 'Partially Paid'),
        ('PAID', 'Fully Paid'),
    ]
    
    # Reference Info
    bill_number = models.CharField(max_length=50, unique=True, db_index=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.PROTECT, related_name='bills')
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE, related_name='vendor_bills')
    
    # Dates
    bill_date = models.DateField(db_index=True)
    due_date = models.DateField(db_index=True)
    received_date = models.DateField(null=True, blank=True)
    
    # Amount Details
    subtotal = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2)
    
    # Payment Tracking
    amount_paid = models.DecimalField(max_digits=15, decimal_places=2, default=0, db_index=True)
    amount_remaining = models.DecimalField(max_digits=15, decimal_places=2)
    
    # Status
    status = models.CharField(max_length=20, choices=BILL_STATUS_CHOICES, default='DRAFT', db_index=True)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='UNPAID', db_index=True)
    
    # Bill Details
    description = models.TextField(blank=True, null=True)
    vendor_po_number = models.CharField(max_length=100, blank=True, null=True)
    reference_number = models.CharField(max_length=100, blank=True, null=True)
    
    # GL Integration
    ap_account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, related_name='vendor_bills_ap')
    expense_account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, blank=True, related_name='vendor_bills_expense')
    
    # Approval Workflow
    is_approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_bills')
    approved_date = models.DateTimeField(null=True, blank=True)
    
    # System Fields
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_bills')
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    # GL Entry Reference
    gl_entry = models.OneToOneField(LedgerEntry, on_delete=models.SET_NULL, null=True, blank=True, related_name='vendor_bill')
    
    class Meta:
        ordering = ['-bill_date']
        indexes = [
            models.Index(fields=['vendor', 'entity']),
            models.Index(fields=['status', 'payment_status']),
            models.Index(fields=['due_date']),
            models.Index(fields=['created_date']),
        ]
    
    def __str__(self):
        return f"{self.bill_number} - {self.vendor.name} - {self.total_amount}"
    
    def calculate_days_overdue(self):
        """Calculate days overdue"""
        if self.status not in ['PAID', 'CANCELLED'] and timezone.now().date() > self.due_date:
            return (timezone.now().date() - self.due_date).days
        return 0
    
    def is_overdue(self):
        """Check if bill is overdue"""
        return self.calculate_days_overdue() > 0
    
    def update_payment_status(self):
        """Update payment status based on amount paid"""
        if self.amount_paid == 0:
            self.payment_status = 'UNPAID'
        elif self.amount_paid < self.total_amount:
            self.payment_status = 'PARTIAL'
        else:
            self.payment_status = 'PAID'
            self.status = 'PAID'
        self.save()


class VendorBillLineItem(models.Model):
    """Line items on vendor bills"""
    
    bill = models.ForeignKey(VendorBill, on_delete=models.CASCADE, related_name='line_items')
    
    # Item Details
    description = models.CharField(max_length=255)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    line_total = models.DecimalField(max_digits=15, decimal_places=2)
    
    # GL Coding
    expense_account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, related_name='bill_line_items')
    cost_center = models.CharField(max_length=50, blank=True, null=True)
    
    # Tax
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    tax_type = models.CharField(max_length=50, blank=True, null=True, help_text="e.g., GST, VAT, Sales Tax, Excise")
    tax_account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, blank=True, related_name='bill_line_taxes', help_text="Input Tax Recoverable or Tax Expense account")
    tax_recoverable = models.BooleanField(default=True, help_text="Is the tax recoverable/creditable?")
    
    # Notes
    notes = models.TextField(blank=True, null=True)
    
    # PO Reference (will be created after procurement app is set up)
    po_line_item = models.ForeignKey('procurement.POLineItem', on_delete=models.SET_NULL, null=True, blank=True, related_name='bill_line_items')
    
    created_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.bill.bill_number} - {self.description}"


class VendorPayment(models.Model):
    """Record of payments made to vendors"""
    
    PAYMENT_METHOD_CHOICES = [
        ('CASH', 'Cash'),
        ('CHECK', 'Check'),
        ('ACH', 'ACH Transfer'),
        ('WIRE', 'Wire Transfer'),
        ('CREDIT_CARD', 'Credit Card'),
        ('OTHER', 'Other'),
    ]
    
    # Payment Info
    payment_number = models.CharField(max_length=50, unique=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.PROTECT, related_name='ap_payments')
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE, related_name='ap_vendor_payments')
    
    # Bills Paid
    bills = models.ManyToManyField(VendorBill, related_name='payments')
    
    # Payment Details
    payment_amount = models.DecimalField(max_digits=15, decimal_places=2)
    payment_date = models.DateField(db_index=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    
    # Bank/Check Info
    bank_account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, related_name='vendor_payments')
    check_number = models.CharField(max_length=50, blank=True, null=True)
    reference_number = models.CharField(max_length=100, blank=True, null=True)
    
    # GL Integration
    gl_entry = models.OneToOneField(LedgerEntry, on_delete=models.SET_NULL, null=True, blank=True, related_name='vendor_payment')
    
    # Approval
    is_approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_payments')
    
    # System Fields
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_payments')
    created_date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-payment_date']
        indexes = [
            models.Index(fields=['vendor', 'entity']),
            models.Index(fields=['payment_date']),
            models.Index(fields=['payment_method']),
        ]
    
    def __str__(self):
        return f"{self.payment_number} - {self.vendor.name} - {self.payment_amount}"


class APDiscount(models.Model):
    """Capture early payment discounts offered by vendors"""
    
    bill = models.OneToOneField(VendorBill, on_delete=models.CASCADE, related_name='discount')
    
    # Discount Terms
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2)  # e.g., 2.00 for 2%
    discount_days = models.IntegerField()  # e.g., 10 for 2/10 Net 30
    full_due_days = models.IntegerField()  # e.g., 30 for 2/10 Net 30
    
    # Discount Amount
    discount_amount = models.DecimalField(max_digits=15, decimal_places=2)
    
    # Status
    discount_taken = models.BooleanField(default=False)
    discount_date = models.DateField(null=True, blank=True)
    
    # GL Integration
    discount_account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, related_name='ap_discounts')
    
    created_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Discount for {self.bill.bill_number} - {self.discount_percentage}%"


class APAging(models.Model):
    """AP Aging report - snapshot of vendor payables by age"""
    
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE, related_name='ap_aging')
    
    # Aging Buckets
    current = models.DecimalField(max_digits=15, decimal_places=2, default=0)  # Due today or later
    days_1_30 = models.DecimalField(max_digits=15, decimal_places=2, default=0)  # 1-30 days overdue
    days_31_60 = models.DecimalField(max_digits=15, decimal_places=2, default=0)  # 31-60 days overdue
    days_61_90 = models.DecimalField(max_digits=15, decimal_places=2, default=0)  # 61-90 days overdue
    days_over_90 = models.DecimalField(max_digits=15, decimal_places=2, default=0)  # Over 90 days
    
    total_outstanding = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Report Date
    report_date = models.DateField(auto_now_add=True)
    
    class Meta:
        ordering = ['-report_date']
        unique_together = ['entity', 'report_date']
    
    def __str__(self):
        return f"AP Aging - {self.entity.name} - {self.report_date}"


class APReconciliation(models.Model):
    """AP Reconciliation - match bills to payments"""
    
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE, related_name='ap_reconciliations')
    bill = models.ForeignKey(VendorBill, on_delete=models.CASCADE, related_name='reconciliations')
    payment = models.ForeignKey(VendorPayment, on_delete=models.CASCADE, related_name='reconciliations')
    
    # Amount
    matched_amount = models.DecimalField(max_digits=15, decimal_places=2)
    
    # Status
    is_matched = models.BooleanField(default=True)
    matched_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['bill', 'payment']
    
    def __str__(self):
        return f"{self.bill.bill_number} - {self.payment.payment_number}"


class APSettings(models.Model):
    """AP module settings per entity"""
    
    entity = models.OneToOneField(Entity, on_delete=models.CASCADE, related_name='ap_settings')
    
    # Default Accounts
    default_ap_account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, related_name='ap_settings_as_default')
    default_expense_account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, blank=True, related_name='ap_settings_default_expense')
    
    # Policies
    require_po_for_bill = models.BooleanField(default=False)  # Require PO before bill posting
    require_approval = models.BooleanField(default=True)  # Require approval before payment
    enable_3way_matching = models.BooleanField(default=False)  # Require PO/Receipt/Bill matching
    
    # Settings
    auto_post_to_gl = models.BooleanField(default=True)  # Auto post bills to GL
    payment_terms_default_days = models.IntegerField(default=30)
    
    # Early Payment Discount
    capture_discounts = models.BooleanField(default=True)
    discount_account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, blank=True, related_name='ap_discount_settings')
    
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"AP Settings - {self.entity.name}"
