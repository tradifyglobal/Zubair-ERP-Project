"""
Sales Module - Pricing Engine
Dynamic pricing calculation with rules and discounts.
"""

from decimal import Decimal
from datetime import date
from django.db.models import Q, Max
from .models import PricingRule, DiscountPolicy, Customer, Quotation, QuotationLine


class PricingEngine:
    """
    Calculates prices based on:
    1. Base product price
    2. Applicable pricing rules (volume, customer, seasonal)
    3. Applicable discount policies
    4. Customer segment discounts
    """
    
    def __init__(self, entity, customer, product=None):
        """
        Initialize pricing engine.
        
        Args:
            entity: The accounting entity
            customer: Customer object
            product: Optional product object (for single product pricing)
        """
        self.entity = entity
        self.customer = customer
        self.product = product
        self.today = date.today()
    
    def calculate_unit_price(self, product, quantity, base_price):
        """
        Calculate final unit price for a product given quantity and customer.
        
        Args:
            product: Product object
            quantity: Decimal quantity
            base_price: Decimal base product price
            
        Returns:
            Decimal final unit price
        """
        # Apply pricing rules (highest priority first)
        applicable_rules = self._get_applicable_rules(product, quantity)
        
        if applicable_rules:
            rule = applicable_rules[0]  # First rule wins (highest priority)
            
            if rule.price_fixed:
                return rule.price_fixed
            elif rule.discount_percent > 0:
                return base_price * (1 - Decimal(rule.discount_percent) / Decimal(100))
        
        return base_price
    
    def calculate_line_discount(self, product, quantity, unit_price, line_total):
        """
        Calculate line-level discount.
        
        Args:
            product: Product object
            quantity: Decimal quantity
            unit_price: Decimal unit price after pricing rules
            line_total: Decimal line subtotal (quantity * unit_price)
            
        Returns:
            Decimal discount amount
        """
        discount_percent = Decimal(0)
        
        # Customer segment discount
        customer_discount = self._get_customer_segment_discount()
        if customer_discount:
            discount_percent += customer_discount
        
        # Applicable discount policies
        policy_discount = self._get_applicable_discount_percent(product, line_total)
        if policy_discount:
            discount_percent += policy_discount
        
        # Cap at 100%
        if discount_percent > 100:
            discount_percent = Decimal(100)
        
        return line_total * (discount_percent / Decimal(100))
    
    def calculate_quotation_price(self, quotation_lines):
        """
        Calculate complete quotation pricing.
        
        Args:
            quotation_lines: List of dict with product, quantity, unit_price
            
        Returns:
            Dict with calculated prices
        """
        subtotal = Decimal(0)
        discount_total = Decimal(0)
        tax_amount = Decimal(0)
        
        for line in quotation_lines:
            product = line['product']
            quantity = Decimal(str(line['quantity']))
            unit_price = Decimal(str(line.get('unit_price', product.base_price or 0)))
            
            # Apply pricing rules
            final_unit_price = self.calculate_unit_price(product, quantity, unit_price)
            
            # Calculate line subtotal
            line_subtotal = quantity * final_unit_price
            
            # Apply line discount
            line_discount = self.calculate_line_discount(product, quantity, final_unit_price, line_subtotal)
            
            subtotal += line_subtotal - line_discount
            discount_total += line_discount
        
        # Calculate tax (simplified - 10% default)
        tax_amount = subtotal * Decimal('0.10')
        total_amount = subtotal + tax_amount
        
        return {
            'subtotal': subtotal,
            'discount_total': discount_total,
            'tax_amount': tax_amount,
            'total_amount': total_amount,
        }
    
    def _get_applicable_rules(self, product, quantity):
        """Get applicable pricing rules sorted by priority."""
        rules = PricingRule.objects.filter(
            entity=self.entity,
            status='ACTIVE',
            effective_from__lte=self.today,
        ).filter(
            Q(effective_to__isnull=True) | Q(effective_to__gte=self.today)
        )
        
        # Filter by product
        rules = rules.filter(
            Q(product__isnull=True) | Q(product=product)
        )
        
        # Filter by customer
        rules = rules.filter(
            Q(customer__isnull=True) | Q(customer=self.customer)
        )
        
        # Filter by customer segment
        customer_segments = self.customer.sales_segments.filter(is_active=True)
        rules = rules.filter(
            Q(customer_segment__isnull=True) | Q(customer_segment__in=customer_segments)
        )
        
        # Filter by quantity range
        rules = rules.filter(
            min_quantity__lte=quantity
        ).filter(
            Q(max_quantity__isnull=True) | Q(max_quantity__gte=quantity)
        )
        
        # Sort by priority (descending) and effective_from (descending)
        return rules.order_by('-priority', '-effective_from')
    
    def _get_customer_segment_discount(self):
        """Get discount from customer's active segments."""
        active_segments = self.customer.sales_segments.filter(is_active=True).order_by('-priority')
        
        if active_segments.exists():
            return Decimal(str(active_segments.first().base_discount_percent))
        
        return Decimal(0)
    
    def _get_applicable_discount_percent(self, product, order_value):
        """Get applicable discount policies for order."""
        policies = DiscountPolicy.objects.filter(
            entity=self.entity,
            is_active=True,
            effective_from__lte=self.today,
        ).filter(
            Q(effective_to__isnull=True) | Q(effective_to__gte=self.today),
            min_order_value__lte=order_value,
        )
        
        # Filter by customer
        policies = policies.filter(
            Q(applicable_customers__isnull=True) | Q(applicable_customers=self.customer)
        )
        
        # Filter by product
        policies = policies.filter(
            Q(applicable_products__isnull=True) | Q(applicable_products=product)
        )
        
        # Get highest discount
        if policies.exists():
            max_discount = policies.aggregate(
                max_discount=Max('discount_percent')
            )
            return Decimal(str(max_discount['max_discount'] or 0))
        
        return Decimal(0)
    
    def get_price_breakdown(self, product, quantity, base_price):
        """
        Get detailed price breakdown for display.
        
        Args:
            product: Product object
            quantity: Decimal quantity
            base_price: Decimal base price
            
        Returns:
            Dict with breakdown
        """
        final_unit_price = self.calculate_unit_price(product, quantity, base_price)
        line_subtotal = quantity * final_unit_price
        
        # Get applied rules and policies
        applied_rules = self._get_applicable_rules(product, quantity)
        customer_discount = self._get_customer_segment_discount()
        
        line_discount = self.calculate_line_discount(product, quantity, final_unit_price, line_subtotal)
        
        return {
            'base_price': base_price,
            'unit_price': final_unit_price,
            'quantity': quantity,
            'line_subtotal': line_subtotal,
            'line_discount': line_discount,
            'line_total': line_subtotal - line_discount,
            'pricing_rules_applied': list(applied_rules.values('rule_code', 'rule_name', 'discount_percent')),
            'customer_segment_discount': customer_discount,
        }


class QuotationManager:
    """Manages quotation operations including creation and conversion."""
    
    @staticmethod
    def create_quotation(entity, customer, quote_data, line_items):
        """
        Create a new quotation.
        
        Args:
            entity: Accounting entity
            customer: Customer object
            quote_data: Dict with quote_number, quote_date, valid_until, etc.
            line_items: List of dicts with product, quantity, unit_price, discount_percent, etc.
            
        Returns:
            Created Quotation object
        """
        quotation = Quotation.objects.create(
            entity=entity,
            customer=customer,
            **quote_data
        )
        
        # Create line items
        for idx, item in enumerate(line_items, 1):
            QuotationLine.objects.create(
                quotation=quotation,
                product=item['product'],
                quantity=Decimal(str(item['quantity'])),
                unit_price=Decimal(str(item.get('unit_price', 0))),
                discount_percent=Decimal(str(item.get('discount_percent', 0))),
                description=item.get('description', ''),
                notes=item.get('notes', ''),
                line_number=idx,
            )
        
        # Calculate totals
        quotation.calculate_totals()
        return quotation
    
    @staticmethod
    def convert_quotation_to_order(quotation, user):
        """
        Convert an accepted quotation to a sales order.
        
        Args:
            quotation: Quotation object
            user: User performing the conversion
            
        Returns:
            Created SalesOrder object
        """
        from .models import SalesOrder, SalesOrderLine
        from django.utils import timezone
        
        if quotation.status != 'ACCEPTED':
            raise ValueError(f"Cannot convert quotation with status: {quotation.status}")
        
        # Create sales order
        sales_order = SalesOrder.objects.create(
            entity=quotation.entity,
            so_number=f"SO-{quotation.quote_number[6:]}",  # Convert quote number to SO
            customer=quotation.customer,
            order_date=timezone.now().date(),
            required_date=quotation.valid_until,
            subtotal=quotation.subtotal,
            tax_amount=quotation.tax_amount,
            total_amount=quotation.total_amount,
            status='CONFIRMED',
            created_by=user,
        )
        
        # Create order lines from quotation lines
        for line in quotation.quotation_lines.all():
            SalesOrderLine.objects.create(
                sales_order=sales_order,
                product=line.product,
                quantity=line.quantity,
                unit_price=line.unit_price,
                discount_percent=line.discount_percent,
                notes=line.notes,
            )
        
        # Update quotation status
        quotation.status = 'CONVERTED'
        quotation.save()
        
        return sales_order
