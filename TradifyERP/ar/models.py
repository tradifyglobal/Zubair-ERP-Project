from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta

from accounting.models import Account, Entity, Currency, Customer


class ARSettings(models.Model):
    """AR configuration at entity level."""
    entity = models.OneToOneField(Entity, on_delete=models.PROTECT)
    require_po_for_invoice = models.BooleanField(default=False)
    require_approval = models.BooleanField(default=True)
    enable_credit_limit_check = models.BooleanField(default=True)
    auto_post_to_gl = models.BooleanField(default=True)
    discount_account = models.ForeignKey(Account, on_delete=models.PROTECT, null=True, blank=True, related_name='ar_discount_settings')
    revenue_account = models.ForeignKey(Account, on_delete=models.PROTECT, null=True, blank=True, related_name='ar_revenue_settings')
    receivable_account = models.ForeignKey(Account, on_delete=models.PROTECT, null=True, blank=True, related_name='ar_receivable_settings')
    
    class Meta:
        verbose_name = 'AR Settings'
        verbose_name_plural = 'AR Settings'
    
    def __str__(self):
        return f"AR Settings - {self.entity.name}"


class CustomerInvoice(models.Model):
    """Customer invoice with GL integration."""
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('ISSUED', 'Issued'),
        ('SENT', 'Sent to Customer'),
        ('PARTIALLY_PAID', 'Partially Paid'),
        ('PAID', 'Paid'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    invoice_number = models.CharField(max_length=50, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name='invoices')
    entity = models.ForeignKey(Entity, on_delete=models.PROTECT)
    invoice_date = models.DateField(default=timezone.now)
    due_date = models.DateField()
    po_number = models.CharField(max_length=50, null=True, blank=True)
    reference_number = models.CharField(max_length=100, null=True, blank=True)
    subject = models.CharField(max_length=200, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT, null=True, blank=True)
    
    # Amounts
    subtotal_amount = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0'))
    tax_amount = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0'))
    total_amount = models.DecimalField(max_digits=15, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0'))
    
    # Status tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    is_approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='ar_invoices_approved')
    approved_date = models.DateTimeField(null=True, blank=True)
    
    # GL integration
    gl_entry_id = models.CharField(max_length=100, null=True, blank=True)
    
    # Audit
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='ar_invoices_created')
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-invoice_date']
        verbose_name = 'Customer Invoice'
        verbose_name_plural = 'Customer Invoices'
        indexes = [
            models.Index(fields=['customer', '-invoice_date']),
            models.Index(fields=['status']),
            models.Index(fields=['entity', 'invoice_date']),
        ]
    
    def __str__(self):
        return f"Invoice {self.invoice_number}"
    
    def get_outstanding_amount(self):
        """Calculate remaining amount due."""
        return self.total_amount - self.amount_paid
    
    def is_overdue(self):
        """Check if invoice is overdue."""
        if self.status in ['PAID', 'CANCELLED']:
            return False
        return timezone.now().date() > self.due_date
    
    def days_outstanding(self):
        """Calculate days outstanding."""
        if self.status in ['PAID', 'CANCELLED']:
            return 0
        return (timezone.now().date() - self.invoice_date).days


class InvoiceLineItem(models.Model):
    """Invoice line items with GL coding."""
    invoice = models.ForeignKey(CustomerInvoice, on_delete=models.CASCADE, related_name='line_items')
    description = models.CharField(max_length=500)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('1'))
    unit_price = models.DecimalField(max_digits=15, decimal_places=2)
    line_total = models.DecimalField(max_digits=15, decimal_places=2)
    
    # GL coding
    revenue_account = models.ForeignKey(Account, on_delete=models.PROTECT, related_name='ar_invoice_lines')
    gl_account = models.ForeignKey(Account, on_delete=models.PROTECT, related_name='ar_invoice_lines_gl', null=True, blank=True)
    cost_center = models.CharField(max_length=100, null=True, blank=True)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0'))
    amount = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0'))
    
    class Meta:
        verbose_name = 'Invoice Line Item'
        verbose_name_plural = 'Invoice Line Items'
    
    def __str__(self):
        return f"{self.invoice.invoice_number} - {self.description}"


class CustomerPayment(models.Model):
    """Customer payment received."""
    PAYMENT_METHOD_CHOICES = [
        ('CASH', 'Cash'),
        ('CHECK', 'Check'),
        ('ACH', 'ACH Transfer'),
        ('WIRE', 'Wire Transfer'),
        ('CREDIT_CARD', 'Credit Card'),
        ('ONLINE', 'Online Payment'),
    ]
    
    payment_number = models.CharField(max_length=50, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name='payments')
    entity = models.ForeignKey(Entity, on_delete=models.PROTECT)
    payment_date = models.DateField(default=timezone.now)
    payment_amount = models.DecimalField(max_digits=15, decimal_places=2)
    amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    invoice = models.ForeignKey(CustomerInvoice, on_delete=models.SET_NULL, null=True, blank=True, related_name='invoice_payments')
    
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    reference_number = models.CharField(max_length=100, null=True, blank=True)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    
    # Multiple invoices can be paid with one payment
    invoices = models.ManyToManyField(CustomerInvoice, through='ARReconciliation', related_name='payments')
    
    # Bank account reference
    bank_account_id = models.CharField(max_length=100, null=True, blank=True)
    
    # GL integration
    gl_entry_id = models.CharField(max_length=100, null=True, blank=True)
    
    # Approval
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='ar_payments_approved')
    approved_date = models.DateTimeField(null=True, blank=True)
    
    # Audit
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='ar_payments_created')
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-payment_date']
        verbose_name = 'Customer Payment'
        verbose_name_plural = 'Customer Payments'
        indexes = [
            models.Index(fields=['customer', '-payment_date']),
            models.Index(fields=['entity', 'payment_date']),
        ]
    
    def __str__(self):
        return f"Payment {self.payment_number}"


class ARDiscount(models.Model):
    """Early payment discount eligibility."""
    invoice = models.OneToOneField(CustomerInvoice, on_delete=models.CASCADE, related_name='discount')
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    discount_days = models.IntegerField(help_text="Days from invoice date to claim discount")
    discount_amount = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0'))
    discount_due_date = models.DateField(null=True, blank=True)
    reason = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=20, null=True, blank=True)
    
    # GL account for discount
    discount_account = models.ForeignKey(Account, on_delete=models.PROTECT, related_name='ar_discounts')
    
    class Meta:
        verbose_name = 'AR Discount'
        verbose_name_plural = 'AR Discounts'
    
    def __str__(self):
        return f"Discount - {self.invoice.invoice_number}"
    
    def is_eligible(self):
        """Check if discount period is still active."""
        cutoff_date = self.invoice.invoice_date + timedelta(days=self.discount_days)
        return timezone.now().date() <= cutoff_date


class ARReconciliation(models.Model):
    """Invoice-to-payment matching."""
    entity = models.ForeignKey(Entity, on_delete=models.PROTECT)
    invoice = models.ForeignKey(CustomerInvoice, on_delete=models.CASCADE, related_name='reconciliations')
    payment = models.ForeignKey(CustomerPayment, on_delete=models.CASCADE, related_name='reconciliations')
    matched_amount = models.DecimalField(max_digits=15, decimal_places=2)
    reconciliation_amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    reconciliation_date = models.DateField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    
    is_matched = models.BooleanField(default=True)
    matched_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('invoice', 'payment')
        verbose_name = 'AR Reconciliation'
        verbose_name_plural = 'AR Reconciliations'
        indexes = [
            models.Index(fields=['entity', 'invoice', 'payment']),
        ]
    
    def __str__(self):
        return f"{self.invoice.invoice_number} - {self.payment.payment_number}"


class ARAging(models.Model):
    """AR aging report snapshot."""
    AGE_BUCKET_CHOICES = [
        ('CURRENT', 'Current (0-30 days)'),
        ('30_60', '31-60 days'),
        ('60_90', '61-90 days'),
        ('90_PLUS', '90+ days'),
    ]
    
    entity = models.ForeignKey(Entity, on_delete=models.PROTECT)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='ar_aging')
    as_of_date = models.DateField(default=timezone.now)
    
    age_bucket = models.CharField(max_length=20, choices=AGE_BUCKET_CHOICES)
    outstanding_amount = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0'))
    invoice_count = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['customer', 'as_of_date', 'age_bucket']
        verbose_name = 'AR Aging'
        verbose_name_plural = 'AR Aging'
        indexes = [
            models.Index(fields=['entity', 'as_of_date']),
            models.Index(fields=['customer', 'as_of_date']),
        ]
    
    def __str__(self):
        return f"{self.customer.customer_name} - {self.age_bucket}"
