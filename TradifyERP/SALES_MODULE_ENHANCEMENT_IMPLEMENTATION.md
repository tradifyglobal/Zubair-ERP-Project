# Sales Module Enhancement - Implementation Guide

**Version:** 1.0  
**Date:** December 6, 2025  
**For:** TradifyERP Sales Module  

---

## Quick Start Implementation

This guide provides step-by-step code to implement the sales module enhancements. Follow the phases in order.

---

## PHASE 1: Models (Quotation, Pricing, Discounts)

### Step 1.1: Add to `sales/models.py`

Add these new models to the end of your existing `sales/models.py`:

```python
# ==================== QUOTATION MODELS ====================

class Quotation(models.Model):
    """Customer quotations/proposals for sales opportunities."""
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
        related_name='sales_quotations'
    )
    
    # Identification
    quote_number = models.CharField(max_length=50, unique=True, db_index=True)
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='quotations'
    )
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
    accepted_date = models.DateField(null=True, blank=True)
    
    # Amounts
    subtotal = models.DecimalField(
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
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    notes = models.TextField(blank=True)
    
    # Audit
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_quotations'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-quote_date']
        indexes = [
            models.Index(fields=['entity', 'created_at']),
            models.Index(fields=['customer', 'status']),
        ]
    
    def __str__(self):
        return f"{self.quote_number} - {self.customer.customer_name}"
    
    def is_expired(self):
        """Check if quotation is expired."""
        return (self.status != 'CONVERTED' and 
                timezone.now().date() > self.valid_until)
    
    def calculate_totals(self):
        """Recalculate quotation totals from line items."""
        lines = self.quote_lines.all()
        self.subtotal = sum(line.line_total for line in lines)
        self.tax_amount = sum(line.tax_amount for line in lines)
        self.total_amount = self.subtotal + self.tax_amount - self.discount_amount
        return self.total_amount


class QuotationLine(models.Model):
    """Individual line items in a quotation."""
    quotation = models.ForeignKey(
        Quotation,
        on_delete=models.CASCADE,
        related_name='quote_lines'
    )
    
    product = models.ForeignKey(
        'manufacturing.Product',
        on_delete=models.PROTECT
    )
    
    # Quantities and pricing
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
    
    # Discounts
    discount_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    discount_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    
    # Taxes
    tax_percent = models.DecimalField(
        max_digits=5,
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
    
    # Totals
    line_total = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    
    # Description
    description = models.TextField(blank=True)
    
    class Meta:
        ordering = ['id']
    
    def __str__(self):
        return f"{self.product.name} - {self.quantity}"
    
    def calculate_totals(self):
        """Calculate line item totals."""
        # Base amount
        base_amount = self.quantity * self.unit_price
        
        # Apply discount
        if self.discount_percent > 0:
            self.discount_amount = (base_amount * self.discount_percent) / 100
        
        # Subtotal after discount
        subtotal = base_amount - self.discount_amount
        
        # Calculate tax
        if self.tax_percent > 0:
            self.tax_amount = (subtotal * self.tax_percent) / 100
        
        # Line total
        self.line_total = subtotal + self.tax_amount
        
        return self.line_total


# ==================== PRICING MODELS ====================

class PricingRule(models.Model):
    """Dynamic pricing rules for products."""
    RULE_TYPE_CHOICES = [
        ('QUANTITY', 'Quantity-based'),
        ('CUSTOMER_TYPE', 'Customer Type'),
        ('PRODUCT_CATEGORY', 'Product Category'),
        ('DATE_RANGE', 'Date Range'),
        ('VOLUME_TIER', 'Volume Tier'),
    ]
    
    PRICING_METHOD_CHOICES = [
        ('PERCENTAGE', 'Percentage Discount'),
        ('FIXED', 'Fixed Discount'),
        ('TIERED', 'Tiered Pricing'),
        ('FIXED_PRICE', 'Fixed Price'),
    ]
    
    entity = models.ForeignKey(
        'accounting.Entity',
        on_delete=models.CASCADE,
        related_name='pricing_rules'
    )
    
    # Basic Info
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    rule_type = models.CharField(max_length=20, choices=RULE_TYPE_CHOICES)
    priority = models.IntegerField(default=100, help_text="Lower number = higher priority")
    
    # Conditions
    min_quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)]
    )
    max_quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)]
    )
    
    customer_type = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        choices=Customer.CUSTOMER_TYPE
    )
    
    product_category = models.ForeignKey(
        'manufacturing.Category',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pricing_rules'
    )
    
    product = models.ForeignKey(
        'manufacturing.Product',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pricing_rules'
    )
    
    # Pricing
    pricing_method = models.CharField(max_length=20, choices=PRICING_METHOD_CHOICES)
    discount_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    new_price = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)]
    )
    
    # Validity
    valid_from = models.DateField(default=timezone.now)
    valid_until = models.DateField(null=True, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['priority', '-created_at']
        indexes = [
            models.Index(fields=['entity', 'is_active']),
            models.Index(fields=['rule_type', 'priority']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.rule_type})"
    
    def applies_to(self, product, customer, quantity):
        """Check if this rule applies to given parameters."""
        from django.utils import timezone as tz
        
        # Check date range
        today = tz.now().date()
        if self.valid_from > today:
            return False
        if self.valid_until and self.valid_until < today:
            return False
        
        # Check rule type conditions
        if self.rule_type == 'QUANTITY':
            if self.min_quantity and quantity < self.min_quantity:
                return False
            if self.max_quantity and quantity > self.max_quantity:
                return False
        
        elif self.rule_type == 'CUSTOMER_TYPE':
            if self.customer_type and customer.customer_type != self.customer_type:
                return False
        
        elif self.rule_type == 'PRODUCT_CATEGORY':
            if self.product_category and product.category != self.product_category:
                return False
        
        elif self.rule_type == 'PRODUCT_CATEGORY' and self.product:
            if product != self.product:
                return False
        
        return True
    
    def calculate_price(self, base_price, quantity):
        """Calculate price after applying rule."""
        if self.pricing_method == 'PERCENTAGE':
            return base_price * (1 - (self.discount_value / 100))
        elif self.pricing_method == 'FIXED':
            return max(0, base_price - self.discount_value)
        elif self.pricing_method == 'FIXED_PRICE':
            return self.new_price or base_price
        return base_price


class DiscountPolicy(models.Model):
    """Discount policies for customers and products."""
    POLICY_TYPE_CHOICES = [
        ('CUSTOMER_TIER', 'Customer Tier'),
        ('VOLUME', 'Volume Discount'),
        ('LOYALTY', 'Loyalty Discount'),
        ('SEASONAL', 'Seasonal'),
        ('PROMOTIONAL', 'Promotional'),
    ]
    
    DISCOUNT_TYPE_CHOICES = [
        ('PERCENTAGE', 'Percentage'),
        ('FIXED', 'Fixed Amount'),
        ('TIERED', 'Tiered'),
    ]
    
    entity = models.ForeignKey(
        'accounting.Entity',
        on_delete=models.CASCADE,
        related_name='discount_policies'
    )
    
    # Basic Info
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    policy_type = models.CharField(max_length=20, choices=POLICY_TYPE_CHOICES)
    
    # Applicability
    customer = models.ForeignKey(
        Customer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='discount_policies'
    )
    
    product = models.ForeignKey(
        'manufacturing.Product',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='discount_policies'
    )
    
    product_category = models.ForeignKey(
        'manufacturing.Category',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='discount_policies'
    )
    
    # Discount Details
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES)
    discount_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    max_discount_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)]
    )
    
    # Validity
    valid_from = models.DateField(default=timezone.now)
    valid_until = models.DateField(null=True, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['entity', 'is_active']),
            models.Index(fields=['customer', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.policy_type})"


class CustomerSegment(models.Model):
    """Customer segmentation for targeted pricing and marketing."""
    entity = models.ForeignKey(
        'accounting.Entity',
        on_delete=models.CASCADE,
        related_name='customer_segments'
    )
    
    # Segment Info
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    # Segmentation Criteria
    min_annual_purchase = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)]
    )
    max_annual_purchase = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)]
    )
    
    customer_type = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        choices=Customer.CUSTOMER_TYPE
    )
    
    geography = models.CharField(max_length=100, blank=True)
    
    # Associated Pricing
    default_discount_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    
    priority = models.IntegerField(default=100, help_text="Lower = higher priority")
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['priority', '-created_at']
        indexes = [
            models.Index(fields=['entity', 'is_active']),
        ]
    
    def __str__(self):
        return self.name
    
    def get_matching_customers(self):
        """Get customers matching this segment criteria."""
        queryset = Customer.objects.filter(entity=self.entity)
        
        if self.customer_type:
            queryset = queryset.filter(customer_type=self.customer_type)
        
        if self.geography:
            queryset = queryset.filter(country__icontains=self.geography)
        
        return queryset


# ==================== SHIPMENT MODELS ====================

class ShipmentOrder(models.Model):
    """Enhanced shipment/delivery tracking."""
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PICKED', 'Picked from Warehouse'),
        ('PACKED', 'Packed'),
        ('SHIPPED', 'Shipped'),
        ('IN_TRANSIT', 'In Transit'),
        ('OUT_FOR_DELIVERY', 'Out for Delivery'),
        ('DELIVERED', 'Delivered'),
        ('RETURNED', 'Returned'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    entity = models.ForeignKey(
        'accounting.Entity',
        on_delete=models.CASCADE,
        related_name='shipment_orders'
    )
    
    # Identification
    shipment_number = models.CharField(max_length=50, unique=True, db_index=True)
    sales_order = models.ForeignKey(
        SalesOrder,
        on_delete=models.CASCADE,
        related_name='shipments'
    )
    warehouse = models.ForeignKey(
        'inventory.Warehouse',
        on_delete=models.SET_NULL,
        null=True
    )
    
    # Dates
    shipment_date = models.DateField(default=timezone.now)
    expected_delivery_date = models.DateField()
    actual_delivery_date = models.DateField(null=True, blank=True)
    
    # Shipping Details
    shipping_method = models.CharField(max_length=100, blank=True)
    carrier_name = models.CharField(max_length=100, blank=True)
    tracking_number = models.CharField(max_length=100, unique=True, db_index=True)
    carrier_reference = models.CharField(max_length=100, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    # Costs
    shipping_cost = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    insurance_cost = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    handling_cost = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    
    # Notes
    notes = models.TextField(blank=True)
    
    # Proof of delivery
    delivery_signature = models.FileField(upload_to='shipments/signatures/', null=True, blank=True)
    delivery_photo = models.ImageField(upload_to='shipments/photos/', null=True, blank=True)
    
    # Audit
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_shipments'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-shipment_date']
        indexes = [
            models.Index(fields=['entity', 'created_at']),
            models.Index(fields=['sales_order', 'status']),
        ]
    
    def __str__(self):
        return f"{self.shipment_number} - {self.tracking_number}"
    
    @property
    def total_shipment_cost(self):
        """Total shipping costs."""
        return self.shipping_cost + self.insurance_cost + self.handling_cost
    
    def is_delivered(self):
        """Check if shipment is delivered."""
        return self.status == 'DELIVERED' and self.actual_delivery_date is not None


class ShipmentTracking(models.Model):
    """Track shipment events and locations."""
    EVENT_CHOICES = [
        ('PICKED', 'Picked from Warehouse'),
        ('PACKED', 'Packed'),
        ('SHIPPED', 'Shipped'),
        ('IN_TRANSIT', 'In Transit'),
        ('DELIVERY_ATTEMPTED', 'Delivery Attempted'),
        ('DELIVERED', 'Delivered'),
        ('RETURNED', 'Returned'),
        ('EXCEPTION', 'Exception/Issue'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    shipment_order = models.ForeignKey(
        ShipmentOrder,
        on_delete=models.CASCADE,
        related_name='tracking_events'
    )
    
    # Event Details
    tracking_event = models.CharField(max_length=30, choices=EVENT_CHOICES)
    event_timestamp = models.DateTimeField(default=timezone.now)
    
    # Location
    location = models.CharField(max_length=255, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    # Details
    description = models.TextField()
    
    # Proof
    photo = models.ImageField(upload_to='shipments/tracking/', null=True, blank=True)
    signature = models.FileField(upload_to='shipments/signatures/', null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    class Meta:
        ordering = ['-event_timestamp']
        indexes = [
            models.Index(fields=['shipment_order', '-event_timestamp']),
        ]
    
    def __str__(self):
        return f"{self.shipment_order.shipment_number} - {self.tracking_event}"
```

### Step 1.2: Create Migration

Run these commands:

```bash
python manage.py makemigrations sales
python manage.py migrate sales
```

---

## PHASE 2: Pricing Engine

### Step 2.1: Create `sales/pricing_engine.py`

```python
"""
Pricing Engine for Dynamic Pricing Rules and Discount Policies
"""

from decimal import Decimal
from django.utils import timezone
from .models import PricingRule, DiscountPolicy, CustomerSegment, Customer


class PricingEngine:
    """Calculate prices based on rules and discounts."""
    
    def __init__(self, entity):
        self.entity = entity
    
    def get_applicable_rules(self, product, customer, quantity):
        """Get all applicable pricing rules."""
        rules = PricingRule.objects.filter(
            entity=self.entity,
            is_active=True
        ).order_by('priority')
        
        applicable = []
        for rule in rules:
            if rule.applies_to(product, customer, quantity):
                applicable.append(rule)
        
        return applicable
    
    def get_applicable_discounts(self, product, customer):
        """Get all applicable discount policies."""
        policies = DiscountPolicy.objects.filter(
            entity=self.entity,
            is_active=True
        )
        
        # Filter by date
        today = timezone.now().date()
        policies = policies.filter(
            valid_from__lte=today
        ).exclude(
            valid_until__lt=today
        )
        
        # Filter by applicability
        applicable = []
        
        # Customer-specific discounts
        customer_discounts = policies.filter(customer=customer)
        applicable.extend(customer_discounts)
        
        # Product-specific discounts
        product_discounts = policies.filter(product=product)
        applicable.extend(product_discounts)
        
        # Category discounts
        if product.category:
            category_discounts = policies.filter(
                product_category=product.category
            )
            applicable.extend(category_discounts)
        
        return applicable
    
    def get_customer_segment_discount(self, customer):
        """Get discount based on customer segment."""
        segment = self._get_customer_segment(customer)
        if segment:
            return segment.default_discount_percent
        return Decimal('0')
    
    def _get_customer_segment(self, customer):
        """Find matching customer segment."""
        segments = CustomerSegment.objects.filter(
            entity=self.entity,
            is_active=True
        ).order_by('priority')
        
        for segment in segments:
            if self._matches_segment(customer, segment):
                return segment
        
        return None
    
    def _matches_segment(self, customer, segment):
        """Check if customer matches segment criteria."""
        if segment.customer_type and customer.customer_type != segment.customer_type:
            return False
        
        if segment.geography and segment.geography not in customer.country:
            return False
        
        # Check purchase history
        if segment.min_annual_purchase or segment.max_annual_purchase:
            annual_purchase = self._get_annual_purchase(customer)
            
            if segment.min_annual_purchase and annual_purchase < segment.min_annual_purchase:
                return False
            
            if segment.max_annual_purchase and annual_purchase > segment.max_annual_purchase:
                return False
        
        return True
    
    def _get_annual_purchase(self, customer):
        """Get annual purchase amount for customer."""
        from .models import Invoice
        from datetime import timedelta
        
        today = timezone.now().date()
        one_year_ago = today - timedelta(days=365)
        
        invoices = Invoice.objects.filter(
            customer=customer,
            created_at__gte=one_year_ago
        )
        
        total = sum(inv.total_amount for inv in invoices)
        return Decimal(total)
    
    def calculate_line_price(self, product, customer, quantity, base_price):
        """Calculate final price for a line item."""
        # Start with base price
        final_price = Decimal(base_price)
        
        # Apply pricing rules (in priority order)
        rules = self.get_applicable_rules(product, customer, quantity)
        for rule in rules:
            final_price = Decimal(rule.calculate_price(final_price, quantity))
        
        # Apply discount policies
        discounts = self.get_applicable_discounts(product, customer)
        for discount in discounts:
            final_price = self._apply_discount(final_price, discount)
        
        # Apply customer segment discount
        segment_discount = self.get_customer_segment_discount(customer)
        if segment_discount:
            final_price = final_price * (1 - (segment_discount / 100))
        
        return max(Decimal('0'), final_price)
    
    def _apply_discount(self, price, policy):
        """Apply a discount policy to price."""
        if policy.discount_type == 'PERCENTAGE':
            discount_amount = price * (policy.discount_value / 100)
        elif policy.discount_type == 'FIXED':
            discount_amount = policy.discount_value
        else:
            discount_amount = Decimal('0')
        
        # Check max discount
        if policy.max_discount_amount:
            discount_amount = min(discount_amount, policy.max_discount_amount)
        
        return price - discount_amount
    
    def get_quote_pricing_breakdown(self, quote):
        """Get detailed pricing breakdown for quotation."""
        breakdown = {
            'lines': [],
            'subtotal': Decimal('0'),
            'total_discounts': Decimal('0'),
            'taxes': Decimal('0'),
            'total': Decimal('0'),
            'rules_applied': [],
        }
        
        for line in quote.quote_lines.all():
            line_breakdown = {
                'product': line.product.name,
                'quantity': line.quantity,
                'base_price': line.unit_price,
                'discount_percent': line.discount_percent,
                'discount_amount': line.discount_amount,
                'tax_percent': line.tax_percent,
                'tax_amount': line.tax_amount,
                'line_total': line.line_total,
            }
            breakdown['lines'].append(line_breakdown)
            breakdown['subtotal'] += line.line_total
        
        breakdown['total'] = quote.total_amount
        
        return breakdown


class QuotationManager:
    """Manage quotation creation and conversion."""
    
    def __init__(self, entity):
        self.entity = entity
        self.pricing_engine = PricingEngine(entity)
    
    def create_quotation_from_opportunity(self, opportunity):
        """Create quotation from CRM opportunity."""
        from .models import Quotation
        
        # Get next quote number
        quote_number = self._generate_quote_number()
        
        quotation = Quotation.objects.create(
            entity=self.entity,
            quote_number=quote_number,
            customer=opportunity.customer,
            opportunity=opportunity,
            created_by=opportunity.created_by,
        )
        
        # Add line items from opportunity products
        # (assuming opportunity has products associated)
        
        return quotation
    
    def convert_quotation_to_order(self, quotation):
        """Convert accepted quotation to sales order."""
        from .models import SalesOrder, SalesOrderLine
        from datetime import timedelta
        from django.utils import timezone
        
        if quotation.status != 'ACCEPTED':
            raise ValueError("Only accepted quotations can be converted to orders")
        
        # Create sales order
        so_number = self._generate_so_number()
        sales_order = SalesOrder.objects.create(
            entity=self.entity,
            so_number=so_number,
            customer=quotation.customer,
            order_date=timezone.now().date(),
            required_date=timezone.now().date() + timedelta(days=14),
            subtotal=quotation.subtotal,
            tax_amount=quotation.tax_amount,
            total_amount=quotation.total_amount,
            created_by=quotation.created_by,
        )
        
        # Convert line items
        for quote_line in quotation.quote_lines.all():
            SalesOrderLine.objects.create(
                sales_order=sales_order,
                product=quote_line.product,
                quantity=quote_line.quantity,
                unit_price=quote_line.unit_price,
                discount_percent=quote_line.discount_percent,
                discount_amount=quote_line.discount_amount,
                tax_amount=quote_line.tax_amount,
                total_amount=quote_line.line_total,
            )
        
        # Update quotation status
        quotation.status = 'CONVERTED'
        quotation.save()
        
        return sales_order
    
    def _generate_quote_number(self):
        """Generate next quotation number."""
        from .models import Quotation
        from datetime import datetime
        
        prefix = f"QT-{datetime.now().strftime('%Y%m')}"
        
        last_quote = Quotation.objects.filter(
            quote_number__startswith=prefix
        ).order_by('quote_number').last()
        
        if last_quote:
            seq = int(last_quote.quote_number.split('-')[-1]) + 1
        else:
            seq = 1
        
        return f"{prefix}-{seq:04d}"
    
    def _generate_so_number(self):
        """Generate next sales order number."""
        from .models import SalesOrder
        from datetime import datetime
        
        prefix = f"SO-{datetime.now().strftime('%Y%m')}"
        
        last_so = SalesOrder.objects.filter(
            so_number__startswith=prefix
        ).order_by('so_number').last()
        
        if last_so:
            seq = int(last_so.so_number.split('-')[-1]) + 1
        else:
            seq = 1
        
        return f"{prefix}-{seq:04d}"
```

---

## PHASE 3: Forms & Views

### Step 3.1: Create `sales/forms.py` additions

Add to your existing forms file:

```python
from django import forms
from .models import Quotation, QuotationLine, PricingRule, DiscountPolicy, CustomerSegment, ShipmentOrder, ShipmentTracking


class QuotationForm(forms.ModelForm):
    class Meta:
        model = Quotation
        fields = ['customer', 'opportunity', 'quote_date', 'valid_until', 'notes']
        widgets = {
            'quote_date': forms.DateInput(attrs={'type': 'date'}),
            'valid_until': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 4}),
        }


class QuotationLineForm(forms.ModelForm):
    class Meta:
        model = QuotationLine
        fields = ['product', 'quantity', 'unit_price', 'discount_percent', 'tax_percent', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 2}),
        }


class PricingRuleForm(forms.ModelForm):
    class Meta:
        model = PricingRule
        fields = [
            'name', 'rule_type', 'priority', 'min_quantity', 'max_quantity',
            'customer_type', 'product_category', 'product', 'pricing_method',
            'discount_value', 'new_price', 'valid_from', 'valid_until', 'is_active'
        ]
        widgets = {
            'valid_from': forms.DateInput(attrs={'type': 'date'}),
            'valid_until': forms.DateInput(attrs={'type': 'date'}),
            'name': forms.TextInput(attrs={'size': 50}),
        }


class DiscountPolicyForm(forms.ModelForm):
    class Meta:
        model = DiscountPolicy
        fields = [
            'name', 'policy_type', 'customer', 'product', 'product_category',
            'discount_type', 'discount_value', 'max_discount_amount',
            'valid_from', 'valid_until', 'is_active'
        ]
        widgets = {
            'valid_from': forms.DateInput(attrs={'type': 'date'}),
            'valid_until': forms.DateInput(attrs={'type': 'date'}),
            'name': forms.TextInput(attrs={'size': 50}),
        }


class CustomerSegmentForm(forms.ModelForm):
    class Meta:
        model = CustomerSegment
        fields = [
            'name', 'description', 'customer_type', 'geography',
            'min_annual_purchase', 'max_annual_purchase',
            'default_discount_percent', 'priority', 'is_active'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class ShipmentOrderForm(forms.ModelForm):
    class Meta:
        model = ShipmentOrder
        fields = [
            'sales_order', 'warehouse', 'shipment_date', 'expected_delivery_date',
            'shipping_method', 'carrier_name', 'tracking_number',
            'shipping_cost', 'insurance_cost', 'handling_cost', 'notes'
        ]
        widgets = {
            'shipment_date': forms.DateInput(attrs={'type': 'date'}),
            'expected_delivery_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }


class ShipmentTrackingForm(forms.ModelForm):
    class Meta:
        model = ShipmentTracking
        fields = ['tracking_event', 'event_timestamp', 'location', 'description', 'photo', 'signature']
        widgets = {
            'event_timestamp': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }
```

---

## PHASE 4: URLs & Views

### Step 4.1: Add URLs to `sales/urls.py`

```python
from django.urls import path
from . import views

urlpatterns = [
    # ... existing patterns ...
    
    # Quotation URLs
    path('quotations/', views.QuotationListView.as_view(), name='quotation-list'),
    path('quotations/create/', views.QuotationCreateView.as_view(), name='quotation-create'),
    path('quotations/<int:pk>/', views.QuotationDetailView.as_view(), name='quotation-detail'),
    path('quotations/<int:pk>/edit/', views.QuotationUpdateView.as_view(), name='quotation-edit'),
    path('quotations/<int:pk>/delete/', views.QuotationDeleteView.as_view(), name='quotation-delete'),
    path('quotations/<int:pk>/convert/', views.ConvertQuotationView.as_view(), name='convert-quotation'),
    
    # Pricing Rules URLs
    path('pricing-rules/', views.PricingRuleListView.as_view(), name='pricing-rule-list'),
    path('pricing-rules/create/', views.PricingRuleCreateView.as_view(), name='pricing-rule-create'),
    path('pricing-rules/<int:pk>/edit/', views.PricingRuleUpdateView.as_view(), name='pricing-rule-edit'),
    path('pricing-rules/<int:pk>/delete/', views.PricingRuleDeleteView.as_view(), name='pricing-rule-delete'),
    
    # Discount Policy URLs
    path('discounts/', views.DiscountPolicyListView.as_view(), name='discount-list'),
    path('discounts/create/', views.DiscountPolicyCreateView.as_view(), name='discount-create'),
    path('discounts/<int:pk>/edit/', views.DiscountPolicyUpdateView.as_view(), name='discount-edit'),
    path('discounts/<int:pk>/delete/', views.DiscountPolicyDeleteView.as_view(), name='discount-delete'),
    
    # Customer Segments URLs
    path('segments/', views.CustomerSegmentListView.as_view(), name='segment-list'),
    path('segments/create/', views.CustomerSegmentCreateView.as_view(), name='segment-create'),
    path('segments/<int:pk>/edit/', views.CustomerSegmentUpdateView.as_view(), name='segment-edit'),
    path('segments/<int:pk>/delete/', views.CustomerSegmentDeleteView.as_view(), name='segment-delete'),
    
    # Shipment URLs
    path('shipments/', views.ShipmentOrderListView.as_view(), name='shipment-list'),
    path('shipments/create/', views.ShipmentOrderCreateView.as_view(), name='shipment-create'),
    path('shipments/<int:pk>/', views.ShipmentOrderDetailView.as_view(), name='shipment-detail'),
    path('shipments/<int:pk>/track/', views.ShipmentTrackingView.as_view(), name='shipment-track'),
]
```

### Step 4.2: Create Basic Views Template (add to `sales/views.py`)

```python
# ==================== QUOTATION VIEWS ====================

@method_decorator(csrf_protect, name='dispatch')
class QuotationListView(SessionEntityMixin, LoginRequiredMixin, ListView):
    model = Quotation
    template_name = 'sales/quotation_list.html'
    context_object_name = 'quotations'
    paginate_by = 50
    
    def get_queryset(self):
        queryset = get_filtered_queryset(Quotation, self.request.user)
        
        # Search filter
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(quote_number__icontains=search) |
                Q(customer__customer_name__icontains=search)
            )
        
        # Status filter
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset.order_by('-created_at')


@method_decorator(csrf_protect, name='dispatch')
class QuotationDetailView(SessionEntityMixin, LoginRequiredMixin, DetailView):
    model = Quotation
    template_name = 'sales/quotation_detail.html'
    context_object_name = 'quotation'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['quote_lines'] = self.object.quote_lines.all()
        
        # Pricing breakdown
        from .pricing_engine import PricingEngine
        engine = PricingEngine(self.request.session.get('entity'))
        context['pricing_breakdown'] = engine.get_quote_pricing_breakdown(self.object)
        
        return context


@method_decorator(csrf_protect, name='dispatch')
class QuotationCreateView(SessionEntityMixin, LoginRequiredMixin, CreateView):
    model = Quotation
    form_class = QuotationForm
    template_name = 'sales/quotation_form.html'
    
    def form_valid(self, form):
        entity = self.get_entity()
        form.instance.entity = entity
        form.instance.created_by = self.request.user
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('sales:quotation-detail', kwargs={'pk': self.object.pk})


@method_decorator(csrf_protect, name='dispatch')
class QuotationUpdateView(SessionEntityMixin, LoginRequiredMixin, UpdateView):
    model = Quotation
    form_class = QuotationForm
    template_name = 'sales/quotation_form.html'
    
    def get_success_url(self):
        return reverse('sales:quotation-detail', kwargs={'pk': self.object.pk})


@method_decorator(csrf_protect, name='dispatch')
class QuotationDeleteView(SessionEntityMixin, LoginRequiredMixin, DeleteView):
    model = Quotation
    template_name = 'sales/quotation_confirm_delete.html'
    success_url = reverse_lazy('sales:quotation-list')


@method_decorator(csrf_protect, name='dispatch')
class ConvertQuotationView(SessionEntityMixin, LoginRequiredMixin, View):
    """Convert accepted quotation to sales order."""
    
    def post(self, request, pk):
        quotation = get_object_or_404(Quotation, pk=pk)
        
        if quotation.status != 'ACCEPTED':
            messages.error(request, 'Only accepted quotations can be converted')
            return redirect('sales:quotation-detail', pk=pk)
        
        try:
            from .pricing_engine import QuotationManager
            entity_id = request.session.get('entity')
            entity = Entity.objects.get(id=entity_id)
            
            manager = QuotationManager(entity)
            sales_order = manager.convert_quotation_to_order(quotation)
            
            messages.success(request, f'Quotation converted to Order {sales_order.so_number}')
            return redirect('sales:salesorder-detail', pk=sales_order.pk)
        
        except Exception as e:
            messages.error(request, f'Error converting quotation: {str(e)}')
            return redirect('sales:quotation-detail', pk=pk)


# ==================== PRICING RULE VIEWS ====================

class PricingRuleListView(SessionEntityMixin, LoginRequiredMixin, ListView):
    model = PricingRule
    template_name = 'sales/pricing_rule_list.html'
    context_object_name = 'rules'
    paginate_by = 50
    
    def get_queryset(self):
        return get_filtered_queryset(PricingRule, self.request.user)


@method_decorator(csrf_protect, name='dispatch')
class PricingRuleCreateView(SessionEntityMixin, LoginRequiredMixin, CreateView):
    model = PricingRule
    form_class = PricingRuleForm
    template_name = 'sales/pricing_rule_form.html'
    
    def form_valid(self, form):
        form.instance.entity = self.get_entity()
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('sales:pricing-rule-list')


# ==================== SHIPMENT VIEWS ====================

class ShipmentOrderListView(SessionEntityMixin, LoginRequiredMixin, ListView):
    model = ShipmentOrder
    template_name = 'sales/shipment_list.html'
    context_object_name = 'shipments'
    paginate_by = 50
    
    def get_queryset(self):
        queryset = get_filtered_queryset(ShipmentOrder, self.request.user)
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        return queryset.order_by('-shipment_date')


class ShipmentOrderDetailView(SessionEntityMixin, LoginRequiredMixin, DetailView):
    model = ShipmentOrder
    template_name = 'sales/shipment_detail.html'
    context_object_name = 'shipment'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tracking_events'] = self.object.tracking_events.all().order_by('-event_timestamp')
        return context
```

---

## PHASE 5: Testing & Deployment

### Step 5.1: Create Test Cases

Create `sales/tests.py`:

```python
from django.test import TestCase, Client
from django.contrib.auth.models import User
from accounting.models import Entity
from .models import Customer, Quotation, PricingRule, DiscountPolicy
from .pricing_engine import PricingEngine
from manufacturing.models import Product


class PricingEngineTestCase(TestCase):
    def setUp(self):
        self.entity = Entity.objects.create(name='Test Entity')
        self.customer = Customer.objects.create(
            entity=self.entity,
            customer_code='CUST001',
            customer_name='Test Customer',
            customer_type='BUSINESS'
        )
        self.product = Product.objects.create(
            name='Test Product',
            selling_price=100
        )
        self.engine = PricingEngine(self.entity)
    
    def test_quantity_based_pricing(self):
        """Test quantity-based pricing rules."""
        rule = PricingRule.objects.create(
            entity=self.entity,
            name='Bulk Discount',
            rule_type='QUANTITY',
            min_quantity=10,
            pricing_method='PERCENTAGE',
            discount_value=10
        )
        
        price = self.engine.calculate_line_price(
            self.product, self.customer, 15, 100
        )
        
        self.assertEqual(price, 90)  # 10% discount
    
    def test_customer_type_pricing(self):
        """Test customer type pricing."""
        rule = PricingRule.objects.create(
            entity=self.entity,
            name='Distributor Discount',
            rule_type='CUSTOMER_TYPE',
            customer_type='DISTRIBUTOR',
            pricing_method='FIXED',
            discount_value=15
        )
        
        # Test with business customer (no discount)
        price = self.engine.calculate_line_price(
            self.product, self.customer, 1, 100
        )
        self.assertEqual(price, 100)
```

---

## NEXT STEPS

1. **Create Templates**: Build HTML templates for quotations, pricing rules, shipments
2. **Add APIs**: Create REST endpoints for mobile/external integration
3. **Create Reports**: Build quotation-to-order conversion reports
4. **Deploy**: Push to production after testing

Run: `git add -A && git commit -m "feat: sales module enhancement phase 1-2"`

---

**Document Version:** 1.0  
**Created:** December 6, 2025  
**Status:** Ready for Implementation
