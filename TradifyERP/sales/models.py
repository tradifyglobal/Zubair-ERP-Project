"""
Sales Module Models
Complete sales order management with customer tracking, invoicing, and GL integration.
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils import timezone
from decimal import Decimal


class Customer(models.Model):
    """Customer information and contact details."""
    CUSTOMER_TYPE = [
        ('INDIVIDUAL', 'Individual'),
        ('BUSINESS', 'Business'),
        ('DISTRIBUTOR', 'Distributor'),
        ('RETAILER', 'Retailer'),
    ]
    
    STATUS = [
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'),
        ('SUSPENDED', 'Suspended'),
    ]
    
    entity = models.ForeignKey(
        'accounting.Entity',
        on_delete=models.CASCADE,
        related_name='sales_customers'
    )
    
    # Basic Info
    customer_code = models.CharField(max_length=50, unique=True, db_index=True)
    customer_name = models.CharField(max_length=255)
    customer_type = models.CharField(max_length=20, choices=CUSTOMER_TYPE, default='BUSINESS')
    
    # Contact Info
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    website = models.URLField(blank=True)
    
    # Address
    billing_address = models.TextField(blank=True)
    shipping_address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True)
    
    # Financial
    credit_limit = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    
    # Tax & Compliance
    tax_id = models.CharField(max_length=50, blank=True)
    is_tax_exempt = models.BooleanField(default=False)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS, default='ACTIVE')
    
    # Notes
    notes = models.TextField(blank=True)
    
    # Audit
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_customers'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['customer_name']
        verbose_name_plural = 'Customers'
    
    def __str__(self):
        return f"{self.customer_code} - {self.customer_name}"


class SalesOrder(models.Model):
    """Sales orders for customers."""
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('CONFIRMED', 'Confirmed'),
        ('PROCESSING', 'Processing'),
        ('SHIPPED', 'Shipped'),
        ('DELIVERED', 'Delivered'),
        ('INVOICED', 'Invoiced'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    PAYMENT_STATUS = [
        ('UNPAID', 'Unpaid'),
        ('PARTIAL', 'Partially Paid'),
        ('PAID', 'Paid'),
        ('OVERDUE', 'Overdue'),
    ]
    
    entity = models.ForeignKey(
        'accounting.Entity',
        on_delete=models.CASCADE,
        related_name='sales_orders'
    )
    
    # Identification
    so_number = models.CharField(max_length=50, unique=True, db_index=True)
    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        related_name='sales_orders'
    )
    
    # Dates
    order_date = models.DateField(default=timezone.now)
    required_date = models.DateField()
    ship_date = models.DateField(null=True, blank=True)
    delivery_date = models.DateField(null=True, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='UNPAID')
    
    # Totals
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
    shipping_cost = models.DecimalField(
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
    
    # Shipping
    shipping_method = models.CharField(max_length=100, blank=True)
    tracking_number = models.CharField(max_length=100, blank=True)
    
    # References
    po_reference = models.CharField(max_length=50, blank=True, help_text='Customer PO number')
    
    # Notes
    notes = models.TextField(blank=True)
    
    # Audit
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_sales_orders'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-order_date']
    
    def __str__(self):
        return f"{self.so_number} - {self.customer.customer_name}"


class SalesOrderLine(models.Model):
    """Individual line items in a sales order."""
    sales_order = models.ForeignKey(
        SalesOrder,
        on_delete=models.CASCADE,
        related_name='line_items'
    )
    
    product = models.ForeignKey(
        'manufacturing.Product',
        on_delete=models.PROTECT
    )
    
    # Quantities
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    
    # Pricing
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
    
    # Notes
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['id']
    
    def save(self, *args, **kwargs):
        # Calculate line total
        self.line_total = self.quantity * self.unit_price * (1 - self.discount_percent / 100)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.sales_order.so_number} - {self.product.product_name}"


class Invoice(models.Model):
    """Customer invoices generated from sales orders."""
    INVOICE_STATUS = [
        ('DRAFT', 'Draft'),
        ('ISSUED', 'Issued'),
        ('PAID', 'Paid'),
        ('PARTIAL', 'Partially Paid'),
        ('CANCELLED', 'Cancelled'),
        ('OVERDUE', 'Overdue'),
    ]
    
    entity = models.ForeignKey(
        'accounting.Entity',
        on_delete=models.CASCADE,
        related_name='invoices'
    )
    
    # Identification
    invoice_number = models.CharField(max_length=50, unique=True, db_index=True)
    sales_order = models.OneToOneField(
        SalesOrder,
        on_delete=models.PROTECT,
        related_name='invoice'
    )
    
    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        related_name='invoices'
    )
    
    # Dates
    invoice_date = models.DateField(default=timezone.now)
    due_date = models.DateField()
    
    # Amounts
    subtotal = models.DecimalField(max_digits=18, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    amount_paid = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    
    # Status
    status = models.CharField(max_length=20, choices=INVOICE_STATUS, default='DRAFT')
    
    # Notes
    notes = models.TextField(blank=True)
    
    # Audit
    issued_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='issued_invoices'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-invoice_date']
    
    def __str__(self):
        return f"{self.invoice_number}"
