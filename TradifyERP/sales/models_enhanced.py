"""
Enhanced Sales Module Models - Comprehensive Integration
Includes all new models for Quotation, Payment, Inventory Reservation,
Dispatch Scheduling, Returns, Discounts, and Revenue Recognition.
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils import timezone
from decimal import Decimal
import json


class Quotation(models.Model):
    """Quotations for customers (CRM-Sales bridge)."""
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('SENT', 'Sent to Customer'),
        ('ACCEPTED', 'Accepted'),
        ('REJECTED', 'Rejected'),
        ('EXPIRED', 'Expired'),
        ('CONVERTED', 'Converted to Order'),
    ]
    
    entity = models.ForeignKey(
        'accounting.Entity',
        on_delete=models.CASCADE,
        related_name='quotations'
    )
    
    # Identification
    quotation_number = models.CharField(max_length=50, unique=True, db_index=True)
    customer = models.ForeignKey(
        'sales.Customer',
        on_delete=models.PROTECT,
        related_name='quotations'
    )
    
    # CRM Reference
    crm_opportunity = models.ForeignKey(
        'crm.Opportunity',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='quotations'
    )
    
    # Dates
    quotation_date = models.DateField(default=timezone.now)
    valid_until = models.DateField()
    validity_days = models.IntegerField(default=30)
    
    # Sales Rep
    sales_rep = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_quotations'
    )
    
    # Amounts
    subtotal = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    tax_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    discount_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    total_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    
    # Status & Tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    conversion_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text="Quote to order conversion percentage"
    )
    
    # Notes
    notes = models.TextField(blank=True)
    terms_and_conditions = models.TextField(blank=True)
    
    # Audit
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_quotations_audit'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-quotation_date']
        verbose_name_plural = 'Quotations'
    
    def __str__(self):
        return f"{self.quotation_number} - {self.customer.customer_name}"
    
    def is_expired(self):
        """Check if quotation has expired."""
        return timezone.now().date() > self.valid_until


class QuotationLineItem(models.Model):
    """Line items for quotations."""
    quotation = models.ForeignKey(
        Quotation,
        on_delete=models.CASCADE,
        related_name='line_items'
    )
    
    product = models.ForeignKey(
        'manufacturing.Product',
        on_delete=models.PROTECT
    )
    
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    
    unit_price = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    
    discount_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    
    line_total = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0
    )
    
    notes = models.TextField(blank=True)
    
    def save(self, *args, **kwargs):
        self.line_total = self.quantity * self.unit_price * (1 - self.discount_percent / 100)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.quotation.quotation_number} - {self.product.product_name}"


class Payment(models.Model):
    """Customer payments against invoices."""
    PAYMENT_METHOD_CHOICES = [
        ('CASH', 'Cash'),
        ('CHECK', 'Check'),
        ('CREDIT_CARD', 'Credit Card'),
        ('BANK_TRANSFER', 'Bank Transfer'),
        ('OTHER', 'Other'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('RECEIVED', 'Received'),
        ('DEPOSITED', 'Deposited'),
        ('CLEARED', 'Cleared'),
        ('DISPUTED', 'Disputed'),
    ]
    
    entity = models.ForeignKey(
        'accounting.Entity',
        on_delete=models.CASCADE,
        related_name='customer_payments'
    )
    
    # Identification
    payment_number = models.CharField(max_length=50, unique=True, db_index=True)
    invoice = models.ForeignKey(
        'sales.Invoice',
        on_delete=models.PROTECT,
        related_name='payments'
    )
    
    customer = models.ForeignKey(
        'sales.Customer',
        on_delete=models.PROTECT,
        related_name='payments'
    )
    
    # Payment Details
    payment_date = models.DateField(default=timezone.now)
    amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default='BANK_TRANSFER'
    )
    
    reference_number = models.CharField(
        max_length=100,
        blank=True,
        help_text='Check number, transaction ID, etc.'
    )
    
    # Bank Details (optional)
    bank_account = models.ForeignKey(
        'accounting.Account',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'account_type': 'ASSET'},
        related_name='received_payments'
    )
    
    # Status & Tracking
    status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='RECEIVED'
    )
    
    # GL Reference
    gl_entry_reference = models.CharField(
        max_length=100,
        blank=True,
        help_text='Reference to GL entry created for this payment'
    )
    
    # Notes
    notes = models.TextField(blank=True)
    
    # Audit
    recorded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='recorded_payments'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-payment_date']
    
    def __str__(self):
        return f"{self.payment_number} - {self.amount}"


class InventoryReservation(models.Model):
    """Inventory reservations for sales orders."""
    RESERVATION_STATUS_CHOICES = [
        ('RESERVED', 'Reserved'),
        ('ALLOCATED', 'Allocated to Warehouse'),
        ('PICKED', 'Picked for Shipment'),
        ('SHIPPED', 'Shipped'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    sales_order = models.ForeignKey(
        'sales.SalesOrder',
        on_delete=models.CASCADE,
        related_name='inventory_reservations'
    )
    
    product = models.ForeignKey(
        'manufacturing.Product',
        on_delete=models.PROTECT,
        related_name='sales_reservations'
    )
    
    # Quantities
    quantity_reserved = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    
    quantity_available_at = models.DateField(
        null=True,
        blank=True,
        help_text='Expected date when inventory will be available'
    )
    
    # Location & Status
    warehouse_location = models.CharField(
        max_length=100,
        blank=True,
        help_text='Warehouse bin/location'
    )
    
    status = models.CharField(
        max_length=20,
        choices=RESERVATION_STATUS_CHOICES,
        default='RESERVED'
    )
    
    # Dates
    reservation_date = models.DateTimeField(auto_now_add=True)
    expected_availability_date = models.DateField(
        null=True,
        blank=True
    )
    
    class Meta:
        ordering = ['sales_order']
    
    def __str__(self):
        return f"Reserve {self.quantity_reserved} {self.product.product_name} for SO {self.sales_order.so_number}"


class DispatchSchedule(models.Model):
    """Shipping and delivery scheduling."""
    DELIVERY_STATUS_CHOICES = [
        ('PENDING', 'Pending Dispatch'),
        ('DISPATCHED', 'Dispatched'),
        ('IN_TRANSIT', 'In Transit'),
        ('DELIVERED', 'Delivered'),
        ('FAILED', 'Delivery Failed'),
        ('RETURNED', 'Returned'),
    ]
    
    sales_order = models.ForeignKey(
        'sales.SalesOrder',
        on_delete=models.CASCADE,
        related_name='dispatch_schedules'
    )
    
    # Shipping Details
    dispatch_date = models.DateField(null=True, blank=True)
    carrier_name = models.CharField(max_length=100, blank=True)
    tracking_number = models.CharField(max_length=100, blank=True, db_index=True)
    
    # Delivery Details
    estimated_delivery_date = models.DateField(null=True, blank=True)
    actual_delivery_date = models.DateField(null=True, blank=True)
    delivery_status = models.CharField(
        max_length=20,
        choices=DELIVERY_STATUS_CHOICES,
        default='PENDING'
    )
    
    # Address & Instructions
    delivery_address = models.TextField()
    special_instructions = models.TextField(blank=True)
    
    # Contacts
    recipient_name = models.CharField(max_length=255, blank=True)
    recipient_phone = models.CharField(max_length=20, blank=True)
    
    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_dispatch_schedules'
    )
    
    class Meta:
        ordering = ['-dispatch_date']
    
    def __str__(self):
        return f"Dispatch {self.sales_order.so_number} - {self.delivery_status}"


class SalesReturn(models.Model):
    """Product returns and credit notes."""
    RETURN_REASON_CHOICES = [
        ('DAMAGED', 'Damaged'),
        ('WRONG_ITEM', 'Wrong Item'),
        ('CHANGE_OF_MIND', 'Change of Mind'),
        ('DEFECTIVE', 'Defective'),
        ('OTHER', 'Other'),
    ]
    
    RETURN_STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('SUBMITTED', 'Submitted'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('PROCESSED', 'Processed'),
        ('REFUNDED', 'Refunded'),
    ]
    
    entity = models.ForeignKey(
        'accounting.Entity',
        on_delete=models.CASCADE,
        related_name='sales_returns'
    )
    
    # Identification
    return_number = models.CharField(max_length=50, unique=True, db_index=True)
    invoice = models.ForeignKey(
        'sales.Invoice',
        on_delete=models.PROTECT,
        related_name='returns'
    )
    
    sales_order = models.ForeignKey(
        'sales.SalesOrder',
        on_delete=models.PROTECT,
        related_name='returns'
    )
    
    customer = models.ForeignKey(
        'sales.Customer',
        on_delete=models.PROTECT,
        related_name='returns'
    )
    
    # Return Details
    return_date = models.DateField(default=timezone.now)
    reason = models.CharField(
        max_length=20,
        choices=RETURN_REASON_CHOICES
    )
    
    quantity_returned = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    
    amount_refunded = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    
    # Credit Note
    credit_note_number = models.CharField(max_length=50, blank=True)
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=RETURN_STATUS_CHOICES,
        default='DRAFT'
    )
    
    # GL Reference
    gl_entry_reference = models.CharField(
        max_length=100,
        blank=True,
        help_text='Reference to GL entry created for this return'
    )
    
    # Notes
    reason_details = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    
    # Audit
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_returns'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-return_date']
    
    def __str__(self):
        return f"{self.return_number} - {self.customer.customer_name}"


class SalesDiscount(models.Model):
    """Sales discounts and promotional adjustments."""
    DISCOUNT_TYPE_CHOICES = [
        ('PERCENTAGE', 'Percentage'),
        ('FIXED_AMOUNT', 'Fixed Amount'),
        ('TIERED', 'Tiered'),
    ]
    
    DISCOUNT_REASON_CHOICES = [
        ('LOYALTY', 'Loyalty'),
        ('BULK_PURCHASE', 'Bulk Purchase'),
        ('PROMOTIONAL', 'Promotional'),
        ('EARLY_PAYMENT', 'Early Payment'),
        ('OTHER', 'Other'),
    ]
    
    sales_order = models.ForeignKey(
        'sales.SalesOrder',
        on_delete=models.CASCADE,
        related_name='discounts'
    )
    
    # Discount Details
    discount_code = models.CharField(max_length=50, blank=True)
    discount_type = models.CharField(
        max_length=20,
        choices=DISCOUNT_TYPE_CHOICES
    )
    
    discount_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    
    discount_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    
    reason = models.CharField(
        max_length=20,
        choices=DISCOUNT_REASON_CHOICES
    )
    
    # GL Reference
    gl_entry_reference = models.CharField(
        max_length=100,
        blank=True,
        help_text='Reference to GL entry created for this discount'
    )
    
    # Notes
    notes = models.TextField(blank=True)
    
    # Audit
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_discounts'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Discount for SO {self.sales_order.so_number}"


class RevenueRecognitionSchedule(models.Model):
    """Revenue recognition scheduling for multi-period recognition."""
    RECOGNITION_METHOD_CHOICES = [
        ('CASH', 'Cash Basis'),
        ('ACCRUAL', 'Accrual Basis'),
        ('PERCENTAGE_OF_COMPLETION', 'Percentage of Completion'),
    ]
    
    invoice = models.ForeignKey(
        'sales.Invoice',
        on_delete=models.CASCADE,
        related_name='recognition_schedules'
    )
    
    recognition_method = models.CharField(
        max_length=30,
        choices=RECOGNITION_METHOD_CHOICES,
        default='ACCRUAL'
    )
    
    # Recognition Details
    period_start_date = models.DateField()
    period_end_date = models.DateField()
    
    amount_to_recognize = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    
    amount_recognized = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    
    # Percentage of Completion (if applicable)
    completion_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)]
    )
    
    # Status & GL Reference
    is_recognized = models.BooleanField(default=False)
    gl_entry_reference = models.CharField(
        max_length=100,
        blank=True,
        help_text='Reference to GL entry created for this recognition'
    )
    
    recognized_date = models.DateTimeField(null=True, blank=True)
    
    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['period_start_date']
    
    def __str__(self):
        return f"Recognition {self.invoice.invoice_number} ({self.period_start_date} to {self.period_end_date})"


class SalesConfiguration(models.Model):
    """Per-entity sales configuration and policies."""
    entity = models.OneToOneField(
        'accounting.Entity',
        on_delete=models.CASCADE,
        related_name='sales_configuration'
    )
    
    # Revenue Recognition
    revenue_recognition_method = models.CharField(
        max_length=30,
        choices=RevenueRecognitionSchedule.RECOGNITION_METHOD_CHOICES,
        default='ACCRUAL'
    )
    
    # AR Management
    auto_invoice_on_shipment = models.BooleanField(
        default=False,
        help_text='Automatically generate invoice when shipment is confirmed'
    )
    
    default_payment_terms = models.IntegerField(
        default=30,
        help_text='Default payment terms in days'
    )
    
    dunning_enabled = models.BooleanField(
        default=True,
        help_text='Enable automated dunning/payment reminders'
    )
    
    # Tax
    tax_authority = models.CharField(
        max_length=100,
        blank=True,
        help_text='Primary tax authority for this entity'
    )
    
    # AR Aging Buckets (JSON for flexibility)
    ar_aging_buckets = models.JSONField(
        default=dict,
        help_text='AR aging analysis buckets in days: {"0-30": 0, "31-60": 1, "61-90": 2, "90+": 3}'
    )
    
    # Discount Policy
    allow_early_payment_discounts = models.BooleanField(default=True)
    early_payment_discount_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=2,
        validators=[MinValueValidator(0)]
    )
    
    early_payment_days = models.IntegerField(
        default=10,
        help_text='Days within which early payment discount applies'
    )
    
    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'Sales Configurations'
    
    def __str__(self):
        return f"Sales Configuration - {self.entity.name}"


class AccountingPolicy(models.Model):
    """Accounting policies and GL account mappings for sales."""
    entity = models.OneToOneField(
        'accounting.Entity',
        on_delete=models.CASCADE,
        related_name='sales_accounting_policy'
    )
    
    # Primary GL Accounts
    ar_account = models.ForeignKey(
        'accounting.Account',
        on_delete=models.PROTECT,
        limit_choices_to={'account_type': 'ASSET'},
        related_name='ar_policy_account'
    )
    
    revenue_account = models.ForeignKey(
        'accounting.Account',
        on_delete=models.PROTECT,
        limit_choices_to={'account_type': 'INCOME'},
        related_name='revenue_policy_account'
    )
    
    tax_account = models.ForeignKey(
        'accounting.Account',
        on_delete=models.PROTECT,
        limit_choices_to={'account_type': 'LIABILITY'},
        related_name='tax_policy_account'
    )
    
    # Adjustment Accounts
    discount_account = models.ForeignKey(
        'accounting.Account',
        on_delete=models.PROTECT,
        limit_choices_to={'account_type': 'EXPENSE'},
        related_name='discount_policy_account'
    )
    
    cogs_account = models.ForeignKey(
        'accounting.Account',
        on_delete=models.PROTECT,
        limit_choices_to={'account_type': 'EXPENSE'},
        related_name='cogs_policy_account'
    )
    
    returns_account = models.ForeignKey(
        'accounting.Account',
        on_delete=models.PROTECT,
        limit_choices_to={'account_type': 'INCOME'},
        related_name='returns_policy_account'
    )
    
    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'Accounting Policies'
    
    def __str__(self):
        return f"Accounting Policy - {self.entity.name}"
