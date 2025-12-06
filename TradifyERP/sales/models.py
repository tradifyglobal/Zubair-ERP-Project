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


# ==================== PHASE 1: QUOTATION & PRICING ====================

class Quotation(models.Model):
    """Customer quotations/proposals."""
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('SENT', 'Sent to Customer'),
        ('ACCEPTED', 'Accepted'),
        ('REJECTED', 'Rejected'),
        ('EXPIRED', 'Expired'),
        ('CONVERTED', 'Converted to Order'),
    ]
    
    VALIDITY_PERIOD = [
        (7, '7 days'),
        (14, '14 days'),
        (30, '30 days'),
        (60, '60 days'),
        (90, '90 days'),
    ]
    
    entity = models.ForeignKey(
        'accounting.Entity',
        on_delete=models.CASCADE,
        related_name='quotations'
    )
    
    # Identification
    quote_number = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        default='TEMP'
    )
    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        related_name='quotations'
    )
    
    # Optional link to CRM opportunity
    opportunity = models.ForeignKey(
        'crm.Opportunity',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='quotations'
    )
    
    # Dates
    quote_date = models.DateField(default=timezone.now)
    valid_until = models.DateField()
    
    # Contact
    contact_person = models.CharField(max_length=255, blank=True)
    contact_email = models.EmailField(blank=True)
    
    # Totals (calculated)
    subtotal = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    discount_total = models.DecimalField(
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
    total_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    
    # Currency
    currency = models.CharField(max_length=3, default='USD')
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    
    # Terms
    payment_terms = models.CharField(max_length=255, blank=True, help_text='e.g., Net 30, 50% deposit')
    validity_days = models.IntegerField(choices=VALIDITY_PERIOD, default=30)
    
    # Notes
    internal_notes = models.TextField(blank=True, help_text='Internal notes not shown to customer')
    customer_notes = models.TextField(blank=True, help_text='Notes visible to customer')
    
    # Audit
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_quotations'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-quote_date']
        verbose_name_plural = 'Quotations'
    
    def __str__(self):
        return f"{self.quote_number} - {self.customer.customer_name}"
    
    def is_expired(self):
        """Check if quotation is expired."""
        from datetime import date
        return self.valid_until < date.today() and self.status not in ['CONVERTED', 'REJECTED']
    
    def calculate_totals(self):
        """Calculate quotation totals from line items."""
        lines = self.quotation_lines.all()
        self.subtotal = sum(line.get_subtotal() for line in lines)
        self.discount_total = sum(line.get_discount() for line in lines)
        self.subtotal -= self.discount_total
        
        # Tax calculation (simplified - 10% default)
        self.tax_amount = self.subtotal * Decimal('0.10')
        self.total_amount = self.subtotal + self.tax_amount
        self.save()


class QuotationLine(models.Model):
    """Line items in a quotation."""
    quotation = models.ForeignKey(
        Quotation,
        on_delete=models.CASCADE,
        related_name='quotation_lines'
    )
    
    product = models.ForeignKey(
        'manufacturing.Product',
        on_delete=models.PROTECT
    )
    
    description = models.TextField(blank=True)
    
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
    
    # Discount
    discount_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0), MinValueValidator(100)]
    )
    discount_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0
    )
    
    line_total = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0
    )
    
    # Notes
    notes = models.TextField(blank=True)
    line_number = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['line_number']
    
    def get_subtotal(self):
        """Calculate subtotal before discount."""
        return self.quantity * self.unit_price
    
    def get_discount(self):
        """Calculate discount amount."""
        subtotal = self.get_subtotal()
        return subtotal * (self.discount_percent / 100)
    
    def calculate_line_total(self):
        """Calculate line total after discount."""
        subtotal = self.get_subtotal()
        discount = self.get_discount()
        self.discount_amount = discount
        self.line_total = subtotal - discount
        return self.line_total
    
    def save(self, *args, **kwargs):
        self.calculate_line_total()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.quotation.quote_number} - Line {self.line_number}"


class PricingRule(models.Model):
    """Dynamic pricing rules for products and customers."""
    RULE_TYPE = [
        ('VOLUME', 'Volume-based'),
        ('TIERED', 'Tiered pricing'),
        ('CUSTOMER', 'Customer-specific'),
        ('SEASONAL', 'Seasonal'),
        ('PROMOTION', 'Promotional'),
    ]
    
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'),
        ('SCHEDULED', 'Scheduled'),
        ('EXPIRED', 'Expired'),
    ]
    
    entity = models.ForeignKey(
        'accounting.Entity',
        on_delete=models.CASCADE,
        related_name='pricing_rules'
    )
    
    # Identification
    rule_code = models.CharField(max_length=50, unique=True, db_index=True)
    rule_name = models.CharField(max_length=255)
    rule_type = models.CharField(max_length=20, choices=RULE_TYPE)
    
    # Scope
    product = models.ForeignKey(
        'manufacturing.Product',
        on_delete=models.CASCADE,
        related_name='pricing_rules',
        null=True,
        blank=True,
        help_text='Leave blank for all products'
    )
    
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='pricing_rules',
        null=True,
        blank=True,
        help_text='Leave blank for all customers'
    )
    
    customer_segment = models.ForeignKey(
        'SalesCustomerSegment',
        on_delete=models.CASCADE,
        related_name='pricing_rules',
        null=True,
        blank=True
    )
    
    # Pricing Configuration
    min_quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=1,
        validators=[MinValueValidator(0.01)]
    )
    max_quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    # Price options (use one)
    price_fixed = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Fixed price for this rule'
    )
    
    discount_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0), MinValueValidator(100)],
        help_text='Percentage discount from base price'
    )
    
    # Validity
    effective_from = models.DateField(default=timezone.now)
    effective_to = models.DateField(null=True, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    priority = models.IntegerField(default=0, help_text='Higher priority rules applied first')
    
    # Audit
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_pricing_rules'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-priority', '-effective_from']
        verbose_name_plural = 'Pricing Rules'
    
    def __str__(self):
        return f"{self.rule_code} - {self.rule_name}"
    
    def is_applicable(self, quantity, customer, product):
        """Check if rule applies to given parameters."""
        from datetime import date
        today = date.today()
        
        # Check status and validity dates
        if self.status != 'ACTIVE':
            return False
        if self.effective_from > today:
            return False
        if self.effective_to and self.effective_to < today:
            return False
        
        # Check quantity range
        if quantity < self.min_quantity:
            return False
        if self.max_quantity and quantity > self.max_quantity:
            return False
        
        # Check customer match
        if self.customer and self.customer != customer:
            return False
        
        # Check product match
        if self.product and self.product != product:
            return False
        
        return True


class DiscountPolicy(models.Model):
    """Discount policies for customers and promotions."""
    POLICY_TYPE = [
        ('CUSTOMER', 'Customer-based'),
        ('PRODUCT', 'Product-based'),
        ('ORDER', 'Order-based'),
        ('SEASONAL', 'Seasonal'),
    ]
    
    entity = models.ForeignKey(
        'accounting.Entity',
        on_delete=models.CASCADE,
        related_name='discount_policies'
    )
    
    # Identification
    policy_code = models.CharField(max_length=50, unique=True, db_index=True)
    policy_name = models.CharField(max_length=255)
    policy_type = models.CharField(max_length=20, choices=POLICY_TYPE)
    
    # Configuration
    description = models.TextField(blank=True)
    discount_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MinValueValidator(100)]
    )
    
    # Applicability
    min_order_value = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    
    applicable_customers = models.ManyToManyField(
        Customer,
        blank=True,
        related_name='discount_policies'
    )
    
    applicable_products = models.ManyToManyField(
        'manufacturing.Product',
        blank=True,
        related_name='discount_policies'
    )
    
    # Validity
    effective_from = models.DateField(default=timezone.now)
    effective_to = models.DateField(null=True, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Audit
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_discount_policies'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-effective_from']
        verbose_name_plural = 'Discount Policies'
    
    def __str__(self):
        return f"{self.policy_code} - {self.policy_name}"


class SalesCustomerSegment(models.Model):
    """Customer segmentation for targeted pricing and promotions."""
    SEGMENT_TYPE = [
        ('ENTERPRISE', 'Enterprise'),
        ('CORPORATE', 'Corporate'),
        ('SME', 'Small/Medium'),
        ('RETAIL', 'Retail'),
        ('DISTRIBUTOR', 'Distributor'),
        ('VIP', 'VIP'),
        ('NEW', 'New Customer'),
    ]
    
    entity = models.ForeignKey(
        'accounting.Entity',
        on_delete=models.CASCADE,
        related_name='sales_customer_segments'
    )
    
    # Identification
    segment_code = models.CharField(max_length=50, unique=True, db_index=True)
    segment_name = models.CharField(max_length=255)
    segment_type = models.CharField(max_length=20, choices=SEGMENT_TYPE)
    
    # Segment Criteria
    description = models.TextField(blank=True)
    min_annual_revenue = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    max_annual_revenue = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    # Benefits
    base_discount_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0), MinValueValidator(100)]
    )
    priority = models.IntegerField(default=0, help_text='Higher priority segments get priority pricing')
    
    # Customers in this segment
    customers = models.ManyToManyField(
        Customer,
        blank=True,
        related_name='sales_segments'
    )
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Audit
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_sales_customer_segments'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-priority', 'segment_name']
        verbose_name_plural = 'Sales Customer Segments'
    
    def __str__(self):
        return f"{self.segment_code} - {self.segment_name}"
