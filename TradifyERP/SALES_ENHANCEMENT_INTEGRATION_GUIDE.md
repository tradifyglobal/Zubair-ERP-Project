# Sales Module Enhancements - Integration Guide

**Date:** December 6, 2025  
**Version:** 1.0  
**Purpose:** Guide for integrating sales module enhancements with existing ERP components

---

## Table of Contents

1. [Integration Architecture](#integration-architecture)
2. [Inventory Integration](#inventory-integration)
3. [Accounting (GL) Integration](#accounting-gl-integration)
4. [CRM Integration](#crm-integration)
5. [Manufacturing Integration](#manufacturing-integration)
6. [Shipment & Logistics Integration](#shipment--logistics-integration)
7. [Workflow Automation](#workflow-automation)
8. [Data Synchronization](#data-synchronization)

---

## Integration Architecture

### Current System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        TradifyERP System                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │     CRM      │  │    SALES     │  │  INVENTORY   │           │
│  │  (Leads,     │  │  (Orders,    │  │  (Stock,     │           │
│  │ Opps, Quote) │  │ Invoices)    │  │  Warehouses) │           │
│  └──────────────┘  └──────────────┘  └──────────────┘           │
│         │                  │                  │                  │
│         └──────────────────┼──────────────────┘                  │
│                            ▼                                     │
│                  ┌─────────────────────┐                        │
│                  │   MANUFACTURING     │                        │
│                  │ (Products, BOM,     │                        │
│                  │  Production Orders) │                        │
│                  └─────────────────────┘                        │
│                            │                                     │
│                            ▼                                     │
│                  ┌─────────────────────┐                        │
│                  │    ACCOUNTING (GL)  │                        │
│                  │ (Revenue, AR, COGS) │                        │
│                  └─────────────────────┘                        │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### Integration Points

| Component | Current | Enhanced | Flow |
|-----------|---------|----------|------|
| CRM | Opportunity ref | Full pipeline | Opportunity → Quotation → Order |
| Inventory | Product ref | Stock check | Reserved stock for orders |
| Manufacturing | Product ref | Production orders | Make-to-order workflow |
| Accounting | GL posting | Enhanced GL | Revenue recognition, COGS |
| Shipment | Basic tracking | Full tracking | Order → Shipment → Delivery |

---

## Inventory Integration

### 1. Stock Availability Check

**Purpose:** Verify product availability before confirming orders

**Implementation:**

```python
# File: sales/inventory_integration.py

from inventory.models import Stock, Warehouse
from decimal import Decimal


class InventoryIntegration:
    """Integration with inventory module for stock management."""
    
    @staticmethod
    def check_stock_availability(product, quantity, warehouse=None):
        """
        Check if product is available in required quantity.
        
        Args:
            product: Manufacturing.Product instance
            quantity: Decimal quantity needed
            warehouse: Optional specific warehouse
            
        Returns:
            {
                'available': bool,
                'available_qty': Decimal,
                'warehouses': {warehouse_id: available_qty}
            }
        """
        if warehouse:
            warehouses = [warehouse]
        else:
            warehouses = Warehouse.objects.filter(is_active=True)
        
        total_available = Decimal('0')
        warehouse_availability = {}
        
        for wh in warehouses:
            try:
                stock = Stock.objects.get(product=product, warehouse=wh)
                available = stock.available_quantity
                warehouse_availability[wh.id] = {
                    'warehouse': wh.name,
                    'available': available,
                    'reserved': stock.reserved_quantity,
                    'on_hand': stock.on_hand_quantity
                }
                total_available += available
            except Stock.DoesNotExist:
                warehouse_availability[wh.id] = {
                    'warehouse': wh.name,
                    'available': Decimal('0'),
                    'reserved': Decimal('0'),
                    'on_hand': Decimal('0')
                }
        
        return {
            'available': total_available >= quantity,
            'available_qty': total_available,
            'required_qty': quantity,
            'warehouse_detail': warehouse_availability
        }
    
    @staticmethod
    def reserve_stock(sales_order):
        """
        Reserve stock for sales order when confirmed.
        
        Args:
            sales_order: SalesOrder instance
        """
        for line_item in sales_order.line_items.all():
            # Find best warehouse with available stock
            warehouse = InventoryIntegration._find_warehouse_for_product(
                line_item.product,
                line_item.quantity
            )
            
            if warehouse:
                stock = Stock.objects.get(
                    product=line_item.product,
                    warehouse=warehouse
                )
                # Reserve stock
                stock.reserved_quantity += line_item.quantity
                stock.save()
                
                # Record movement
                from inventory.models import StockMovement
                StockMovement.objects.create(
                    product=line_item.product,
                    warehouse=warehouse,
                    movement_type='RESERVED',
                    quantity=line_item.quantity,
                    reference_number=sales_order.so_number,
                    notes=f'Reserved for SO {sales_order.so_number}'
                )
    
    @staticmethod
    def release_reserved_stock(sales_order):
        """Release reserved stock if order is cancelled."""
        from inventory.models import StockMovement
        
        for line_item in sales_order.line_items.all():
            movements = StockMovement.objects.filter(
                product=line_item.product,
                reference_number=sales_order.so_number,
                movement_type='RESERVED'
            )
            
            for movement in movements:
                # Release reservation
                stock = Stock.objects.get(
                    product=movement.product,
                    warehouse=movement.warehouse
                )
                stock.reserved_quantity -= movement.quantity
                stock.save()
                
                # Create reversal movement
                StockMovement.objects.create(
                    product=line_item.product,
                    warehouse=movement.warehouse,
                    movement_type='RELEASED',
                    quantity=-movement.quantity,
                    reference_number=sales_order.so_number,
                    notes=f'Released from SO {sales_order.so_number} (Cancelled)'
                )
    
    @staticmethod
    def update_stock_on_shipment(shipment):
        """
        Update stock levels when shipment is confirmed.
        Reduce on_hand quantity.
        """
        from inventory.models import StockMovement
        
        for line_item in shipment.sales_order.line_items.all():
            stock = Stock.objects.get(
                product=line_item.product,
                warehouse=shipment.warehouse
            )
            
            # Reduce on_hand (goods physically leaving warehouse)
            stock.on_hand_quantity -= line_item.quantity
            stock.reserved_quantity -= line_item.quantity
            stock.save()
            
            # Record movement
            StockMovement.objects.create(
                product=line_item.product,
                warehouse=shipment.warehouse,
                movement_type='SHIPPED',
                quantity=-line_item.quantity,
                reference_number=shipment.shipment_number,
                notes=f'Shipped via shipment {shipment.shipment_number}'
            )
    
    @staticmethod
    def _find_warehouse_for_product(product, quantity):
        """Find warehouse with available stock."""
        from inventory.models import Stock
        
        stocks = Stock.objects.filter(
            product=product,
            available_quantity__gte=quantity
        ).order_by('-available_quantity')
        
        if stocks.exists():
            return stocks.first().warehouse
        
        return None
```

### 2. Order Confirmation Signal

**Add to `sales/signals.py`:**

```python
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import SalesOrder
from .inventory_integration import InventoryIntegration


@receiver(post_save, sender=SalesOrder)
def handle_sales_order_status_change(sender, instance, created, **kwargs):
    """Handle inventory updates based on sales order status."""
    
    if instance.status == 'CONFIRMED':
        # Check stock and reserve
        for line_item in instance.line_items.all():
            availability = InventoryIntegration.check_stock_availability(
                line_item.product,
                line_item.quantity
            )
            
            if not availability['available']:
                # Could trigger backorder workflow
                pass
        
        # Reserve stock
        InventoryIntegration.reserve_stock(instance)
    
    elif instance.status == 'CANCELLED':
        # Release reserved stock
        InventoryIntegration.release_reserved_stock(instance)
    
    elif instance.status == 'SHIPPED':
        # Update stock levels
        for shipment in instance.shipments.all():
            if shipment.status == 'SHIPPED':
                InventoryIntegration.update_stock_on_shipment(shipment)


# In apps.py
def ready(self):
    import sales.signals
```

---

## Accounting (GL) Integration

### 1. Enhanced Revenue Recognition

**Purpose:** Record revenue when shipment is confirmed (not invoice date)

**Implementation:**

```python
# File: sales/gl_integration_enhanced.py

from accounting.models import GLEntry, GLAccount
from decimal import Decimal
from django.utils import timezone


class EnhancedGLIntegration:
    """Enhanced GL integration with revenue recognition."""
    
    @staticmethod
    def create_shipment_gl_entries(shipment):
        """
        Create GL entries when shipment is confirmed.
        Revenue recognized on shipment (shipping date), not invoice date.
        COGS recognized simultaneously.
        
        Journal Entry:
            Debit: Cash in Transit / Accounts Receivable
            Credit: Sales Revenue
            
            Debit: Cost of Goods Sold (COGS)
            Credit: Inventory
        """
        sales_order = shipment.sales_order
        invoice = sales_order.invoice
        
        if not invoice or invoice.status != 'ISSUED':
            return  # Only if invoice exists and is issued
        
        # Get GL accounts
        ar_account = GLAccount.objects.get(
            entity=sales_order.entity,
            account_type='ASSET',
            code='1200'  # Accounts Receivable
        )
        
        revenue_account = GLAccount.objects.get(
            entity=sales_order.entity,
            account_type='REVENUE',
            code='4100'  # Sales Revenue
        )
        
        cogs_account = GLAccount.objects.get(
            entity=sales_order.entity,
            account_type='EXPENSE',
            code='5100'  # Cost of Goods Sold
        )
        
        inventory_account = GLAccount.objects.get(
            entity=sales_order.entity,
            account_type='ASSET',
            code='1300'  # Inventory
        )
        
        # Calculate COGS
        total_cogs = Decimal('0')
        for line_item in sales_order.line_items.all():
            # Get product cost price
            product_cost = line_item.product.cost_price
            line_cogs = line_item.quantity * product_cost
            total_cogs += line_cogs
        
        # Entry 1: AR / Revenue (if not already posted)
        if not GLEntry.objects.filter(
            reference_number=invoice.invoice_number,
            entry_type='INVOICE'
        ).exists():
            GLEntry.objects.create(
                entity=sales_order.entity,
                date=shipment.shipment_date,
                reference_number=invoice.invoice_number,
                entry_type='INVOICE',
                description=f'Revenue recognition for {invoice.invoice_number}',
                
                debit_account=ar_account,
                debit_amount=invoice.total_amount,
                
                credit_account=revenue_account,
                credit_amount=invoice.total_amount,
                
                created_by_module='SALES',
                status='POSTED'
            )
        
        # Entry 2: COGS / Inventory
        GLEntry.objects.create(
            entity=sales_order.entity,
            date=shipment.shipment_date,
            reference_number=f"{shipment.shipment_number}-COGS",
            entry_type='COGS',
            description=f'COGS recognition for shipment {shipment.shipment_number}',
            
            debit_account=cogs_account,
            debit_amount=total_cogs,
            
            credit_account=inventory_account,
            credit_amount=total_cogs,
            
            created_by_module='SALES',
            status='POSTED'
        )
        
        return True
    
    @staticmethod
    def create_payment_gl_entries(payment):
        """
        Create GL entries when payment is received.
        
        Journal Entry:
            Debit: Cash (Bank Account)
            Credit: Accounts Receivable
        """
        from .models import Invoice
        
        invoice = payment.invoice
        
        cash_account = GLAccount.objects.get(
            entity=invoice.entity,
            account_type='ASSET',
            code='1000'  # Bank Cash
        )
        
        ar_account = GLAccount.objects.get(
            entity=invoice.entity,
            account_type='ASSET',
            code='1200'  # AR
        )
        
        GLEntry.objects.create(
            entity=invoice.entity,
            date=payment.payment_date,
            reference_number=payment.reference_number,
            entry_type='PAYMENT',
            description=f'Payment received for {invoice.invoice_number}',
            
            debit_account=cash_account,
            debit_amount=payment.amount,
            
            credit_account=ar_account,
            credit_amount=payment.amount,
            
            created_by_module='SALES',
            status='POSTED'
        )
    
    @staticmethod
    def reverse_gl_entries(invoice):
        """Reverse GL entries if invoice is cancelled."""
        entries = GLEntry.objects.filter(
            reference_number=invoice.invoice_number
        )
        
        for entry in entries:
            # Create reversal entry
            GLEntry.objects.create(
                entity=entry.entity,
                date=timezone.now().date(),
                reference_number=f"{invoice.invoice_number}-REVERSAL",
                entry_type=entry.entry_type,
                description=f'Reversal of {entry.reference_number}',
                
                debit_account=entry.credit_account,
                debit_amount=entry.credit_amount,
                
                credit_account=entry.debit_account,
                credit_amount=entry.debit_amount,
                
                created_by_module='SALES',
                status='POSTED'
            )
            
            # Mark original as reversed
            entry.status = 'REVERSED'
            entry.save()
```

### 2. Tax Integration

**Track and report sales taxes:**

```python
# Add to GL integration

class TaxIntegration:
    """Handle sales tax tracking and GL posting."""
    
    @staticmethod
    def create_tax_gl_entries(invoice):
        """Create GL entry for sales tax."""
        
        if invoice.tax_amount <= 0:
            return
        
        tax_payable_account = GLAccount.objects.get(
            entity=invoice.entity,
            account_type='LIABILITY',
            code='2100'  # Sales Tax Payable
        )
        
        GLEntry.objects.create(
            entity=invoice.entity,
            date=invoice.created_at.date(),
            reference_number=invoice.invoice_number,
            entry_type='TAX',
            description=f'Sales tax for {invoice.invoice_number}',
            
            debit_account=ar_account,  # Part of total AR
            debit_amount=invoice.tax_amount,
            
            credit_account=tax_payable_account,
            credit_amount=invoice.tax_amount,
            
            created_by_module='SALES',
            status='POSTED'
        )
    
    @staticmethod
    def get_tax_summary(entity, from_date, to_date):
        """Get tax collected for filing."""
        entries = GLEntry.objects.filter(
            entity=entity,
            entry_type='TAX',
            date__range=[from_date, to_date],
            status='POSTED'
        )
        
        total_tax = sum(e.credit_amount for e in entries)
        
        return {
            'total_tax_collected': total_tax,
            'entry_count': entries.count(),
            'period': f"{from_date} to {to_date}"
        }
```

---

## CRM Integration

### 1. Opportunity to Quotation Workflow

**Purpose:** Bridge CRM opportunities with sales quotations

**Implementation:**

```python
# File: sales/crm_integration.py

from crm.models import Opportunity, Lead, Activity
from .models import Quotation, SalesOrder, Customer
from .pricing_engine import PricingEngine
from django.db import transaction


class CRMIntegration:
    """Integrate sales module with CRM for complete sales pipeline."""
    
    @staticmethod
    @transaction.atomic
    def create_quotation_from_opportunity(opportunity, user):
        """
        Create quotation from CRM opportunity.
        Links lead → opportunity → quotation → order
        
        Args:
            opportunity: crm.Opportunity instance
            user: User creating the quotation
        """
        
        # Get or create customer from opportunity
        customer = CRMIntegration._get_customer_from_opportunity(opportunity)
        
        # Generate quotation
        quote_number = CRMIntegration._generate_quote_number(opportunity.entity)
        
        quotation = Quotation.objects.create(
            entity=opportunity.entity,
            quote_number=quote_number,
            customer=customer,
            opportunity=opportunity,
            created_by=user,
            notes=f'From opportunity {opportunity.name}'
        )
        
        # Add line items from opportunity products
        if hasattr(opportunity, 'products'):  # If CRM has product association
            for product in opportunity.products.all():
                from .models import QuotationLine
                from decimal import Decimal
                
                QuotationLine.objects.create(
                    quotation=quotation,
                    product=product,
                    quantity=Decimal('1'),
                    unit_price=product.selling_price,
                    description=f'From {opportunity.name}'
                )
        
        # Create activity for follow-up
        Activity.objects.create(
            entity=opportunity.entity,
            opportunity=opportunity,
            activity_type='QUOTE',
            subject=f'Quotation {quote_number} created',
            description=f'Sales team created quotation based on this opportunity',
            due_date=timezone.now().date() + timedelta(days=7),
            created_by=user
        )
        
        # Update opportunity status
        opportunity.status = 'QUOTE_SENT'
        opportunity.save()
        
        return quotation
    
    @staticmethod
    def convert_quotation_to_opportunity(quotation):
        """
        Link accepted quotation to opportunity and update pipeline.
        """
        if quotation.opportunity:
            opportunity = quotation.opportunity
            opportunity.status = 'WON'
            opportunity.save()
    
    @staticmethod
    def sync_sales_to_crm(sales_order, user):
        """
        Sync created sales order back to CRM as won opportunity.
        Creates activity log entry.
        """
        if sales_order.quotation and sales_order.quotation.opportunity:
            opportunity = sales_order.quotation.opportunity
            
            # Update opportunity
            opportunity.status = 'WON'
            opportunity.deal_amount = sales_order.total_amount
            opportunity.save()
            
            # Log activity
            Activity.objects.create(
                entity=sales_order.entity,
                opportunity=opportunity,
                activity_type='DEAL_WON',
                subject=f'Deal won - Order {sales_order.so_number}',
                description=f'Sales order created with value ${sales_order.total_amount}',
                created_by=user
            )
    
    @staticmethod
    def track_quotation_metrics(opportunity):
        """
        Track conversion metrics for CRM reporting.
        """
        quotations = Quotation.objects.filter(opportunity=opportunity)
        
        return {
            'total_quotations': quotations.count(),
            'accepted': quotations.filter(status='ACCEPTED').count(),
            'rejected': quotations.filter(status='REJECTED').count(),
            'expired': quotations.filter(status='EXPIRED').count(),
            'conversion_rate': (
                quotations.filter(status='ACCEPTED').count() / 
                quotations.count() * 100
                if quotations.exists() else 0
            )
        }
    
    @staticmethod
    def _get_customer_from_opportunity(opportunity):
        """Get or create customer from opportunity."""
        # Logic to link CRM contact to sales customer
        if hasattr(opportunity, 'customer'):
            return opportunity.customer
        else:
            # Create new customer from opportunity
            from crm.models import Contact
            contact = opportunity.contact if hasattr(opportunity, 'contact') else None
            
            return Customer.objects.get_or_create(
                entity=opportunity.entity,
                customer_code=f"OPP-{opportunity.id}",
                defaults={
                    'customer_name': opportunity.name,
                    'email': contact.email if contact else '',
                    'phone': contact.phone if contact else '',
                    'customer_type': 'BUSINESS',
                }
            )[0]
    
    @staticmethod
    def _generate_quote_number(entity):
        """Generate unique quotation number."""
        from datetime import datetime
        prefix = f"QT-{datetime.now().strftime('%Y%m')}"
        
        last_quote = Quotation.objects.filter(
            entity=entity,
            quote_number__startswith=prefix
        ).order_by('quote_number').last()
        
        if last_quote:
            seq = int(last_quote.quote_number.split('-')[-1]) + 1
        else:
            seq = 1
        
        return f"{prefix}-{seq:04d}"
```

### 2. Lead Scoring Based on Sales History

```python
# Add to CRM integration

@staticmethod
def calculate_lead_score_from_sales(lead):
    """
    Calculate lead score based on sales history.
    High-value customers get higher score.
    """
    from .models import SalesOrder, Invoice
    from crm.models import Lead
    
    customer = lead.customer if hasattr(lead, 'customer') else None
    if not customer:
        return 0
    
    score = 0
    
    # Historical purchases
    total_purchases = SalesOrder.objects.filter(
        customer=customer
    ).count()
    score += min(total_purchases * 10, 50)  # Max 50 points
    
    # Purchase value
    total_value = Invoice.objects.filter(
        customer=customer
    ).aggregate(sum=models.Sum('total_amount'))['sum'] or 0
    
    if total_value > 10000:
        score += 40
    elif total_value > 5000:
        score += 25
    elif total_value > 1000:
        score += 10
    
    # Recent activity
    recent_invoices = Invoice.objects.filter(
        customer=customer,
        created_at__gte=timezone.now() - timedelta(days=90)
    ).count()
    
    if recent_invoices > 0:
        score += 15
    
    return min(score, 100)  # Cap at 100
```

---

## Manufacturing Integration

### 1. Production Order Creation from Sales Orders

```python
# File: sales/manufacturing_integration.py

from manufacturing.models import ProductionOrder, ProductionOrderLine
from .models import SalesOrder
from datetime import timedelta
from django.utils import timezone


class ManufacturingIntegration:
    """Link sales orders with manufacturing."""
    
    @staticmethod
    def create_production_orders_from_sales(sales_order):
        """
        Create production orders for make-to-order items.
        
        Args:
            sales_order: SalesOrder instance
        """
        production_orders = []
        
        for line_item in sales_order.line_items.all():
            product = line_item.product
            
            # Check if make-to-order
            if not product.is_make_to_stock:
                # Create production order
                po = ProductionOrder.objects.create(
                    entity=sales_order.entity,
                    po_number=ManufacturingIntegration._generate_po_number(
                        sales_order.entity
                    ),
                    product=product,
                    quantity=line_item.quantity,
                    required_date=sales_order.required_date,
                    source_so_number=sales_order.so_number,
                    status='PLANNED',
                    created_by=sales_order.created_by
                )
                
                production_orders.append(po)
                
                # Create line items from BOM
                if product.bill_of_materials:
                    for bom_line in product.bill_of_materials.lines.all():
                        ProductionOrderLine.objects.create(
                            production_order=po,
                            component=bom_line.component,
                            quantity_required=bom_line.quantity * line_item.quantity,
                            quantity_issued=0
                        )
        
        return production_orders
    
    @staticmethod
    def update_production_status(production_order, new_status):
        """Update production order and notify sales."""
        production_order.status = new_status
        production_order.save()
        
        # Create activity
        if hasattr(production_order, 'source_so_number'):
            # Could trigger event notification
            pass
    
    @staticmethod
    def _generate_po_number(entity):
        """Generate production order number."""
        from datetime import datetime
        prefix = f"PO-{datetime.now().strftime('%Y%m')}"
        
        last_po = ProductionOrder.objects.filter(
            entity=entity,
            po_number__startswith=prefix
        ).order_by('po_number').last()
        
        if last_po:
            seq = int(last_po.po_number.split('-')[-1]) + 1
        else:
            seq = 1
        
        return f"{prefix}-{seq:04d}"
```

---

## Shipment & Logistics Integration

### 1. Carrier Integration Framework

```python
# File: sales/logistics_integration.py

from .models import ShipmentOrder, ShipmentTracking
from decimal import Decimal
from django.utils import timezone


class CarrierIntegration:
    """Framework for carrier/logistics integration."""
    
    CARRIER_PROVIDERS = {
        'FEDEX': 'FedEx',
        'UPS': 'UPS',
        'DHL': 'DHL',
        'LOCAL': 'Local Courier',
        'CUSTOM': 'Custom Carrier'
    }
    
    @staticmethod
    def get_shipping_rates(shipment):
        """
        Get shipping rates from multiple carriers.
        Returns best options.
        """
        rates = {
            'FEDEX': {'rate': Decimal('25.50'), 'days': 2},
            'UPS': {'rate': Decimal('22.75'), 'days': 3},
            'DHL': {'rate': Decimal('28.00'), 'days': 2},
        }
        
        # Integration point: Call actual carrier APIs
        # rates = FedexCarrier.get_rates(shipment)
        
        return rates
    
    @staticmethod
    def create_shipment_label(shipment):
        """
        Create shipment label and get tracking number.
        Integration point for carrier APIs.
        """
        # TODO: Integrate with carrier APIs
        # Placeholder implementation
        
        tracking_number = f"{shipment.shipment_number}-{timezone.now().timestamp()}"
        shipment.tracking_number = tracking_number
        shipment.save()
        
        return {
            'tracking_number': tracking_number,
            'label': None,  # Would contain PDF or image
            'status': 'CREATED'
        }
    
    @staticmethod
    def track_shipment(tracking_number):
        """
        Get real-time tracking updates from carrier.
        """
        # Integration point: Call carrier tracking APIs
        
        shipment = ShipmentOrder.objects.get(tracking_number=tracking_number)
        
        # This would call carrier API
        # events = FedexCarrier.track(tracking_number)
        
        return {
            'tracking_number': tracking_number,
            'status': shipment.status,
            'current_location': 'Distribution Center',
            'events': []
        }
    
    @staticmethod
    def update_tracking_status(shipment, event_data):
        """
        Update shipment tracking with new event from carrier.
        """
        
        # Create tracking event
        ShipmentTracking.objects.create(
            shipment_order=shipment,
            tracking_event=event_data['event'],
            event_timestamp=event_data['timestamp'],
            location=event_data.get('location', ''),
            description=event_data.get('description', ''),
            latitude=event_data.get('latitude'),
            longitude=event_data.get('longitude')
        )
        
        # Update shipment status
        status_map = {
            'PICKED': 'PICKED',
            'PACKED': 'PACKED',
            'SHIPPED': 'SHIPPED',
            'IN_TRANSIT': 'IN_TRANSIT',
            'OUT_FOR_DELIVERY': 'OUT_FOR_DELIVERY',
            'DELIVERED': 'DELIVERED'
        }
        
        if event_data['event'] in status_map:
            shipment.status = status_map[event_data['event']]
            
            if event_data['event'] == 'DELIVERED':
                shipment.actual_delivery_date = event_data['timestamp'].date()
            
            shipment.save()
```

---

## Workflow Automation

### 1. Order Status Workflows

```python
# File: sales/workflows.py

from django.core.mail import send_mail
from django.template.loader import render_to_string
from .models import SalesOrder, Invoice, ShipmentOrder


class OrderWorkflow:
    """Automate order status transitions and notifications."""
    
    @staticmethod
    def process_order_confirmation(sales_order):
        """
        Workflow:
        1. Validate stock availability
        2. Reserve inventory
        3. Create production orders (if needed)
        4. Send confirmation to customer
        5. Notify warehouse
        """
        
        # 1. Check inventory
        from .inventory_integration import InventoryIntegration
        for line_item in sales_order.line_items.all():
            availability = InventoryIntegration.check_stock_availability(
                line_item.product,
                line_item.quantity
            )
            if not availability['available']:
                # Backorder logic
                pass
        
        # 2. Reserve stock
        InventoryIntegration.reserve_stock(sales_order)
        
        # 3. Create production orders
        from .manufacturing_integration import ManufacturingIntegration
        ManufacturingIntegration.create_production_orders_from_sales(sales_order)
        
        # 4. Send customer confirmation
        OrderWorkflow._send_order_confirmation_email(sales_order)
        
        # 5. Notify warehouse
        OrderWorkflow._notify_warehouse(sales_order)
        
        # Update status
        sales_order.status = 'CONFIRMED'
        sales_order.save()
    
    @staticmethod
    def process_order_shipment(shipment):
        """
        Workflow:
        1. Pick items from warehouse
        2. Pack shipment
        3. Generate shipping label
        4. Create GL COGS entries
        5. Send tracking to customer
        """
        
        # 1-3. Fulfillment steps
        shipment.status = 'PACKED'
        shipment.save()
        
        # 4. GL entries for COGS
        from .gl_integration_enhanced import EnhancedGLIntegration
        EnhancedGLIntegration.create_shipment_gl_entries(shipment)
        
        # 5. Send tracking email
        OrderWorkflow._send_shipment_notification(shipment)
        
        shipment.status = 'SHIPPED'
        shipment.save()
    
    @staticmethod
    def process_payment(invoice, payment_amount):
        """
        Workflow:
        1. Record payment
        2. Create GL entry
        3. Update AR
        4. Send receipt to customer
        5. Check if fully paid
        """
        
        from .models import InvoicePayment
        from .gl_integration_enhanced import EnhancedGLIntegration
        
        # 1. Record payment
        payment = InvoicePayment.objects.create(
            invoice=invoice,
            amount=payment_amount,
            payment_date=timezone.now().date()
        )
        
        # 2-3. GL posting
        EnhancedGLIntegration.create_payment_gl_entries(payment)
        
        # 4. Send receipt
        OrderWorkflow._send_payment_receipt(invoice, payment)
        
        # 5. Update invoice status
        total_paid = invoice.payments.aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        if total_paid >= invoice.total_amount:
            invoice.payment_status = 'PAID'
        else:
            invoice.payment_status = 'PARTIAL'
        
        invoice.save()
    
    @staticmethod
    def _send_order_confirmation_email(sales_order):
        """Send order confirmation to customer."""
        try:
            context = {
                'order': sales_order,
                'customer': sales_order.customer,
                'items': sales_order.line_items.all(),
            }
            
            html_message = render_to_string(
                'sales/emails/order_confirmation.html',
                context
            )
            
            send_mail(
                subject=f'Order Confirmation - {sales_order.so_number}',
                message='',
                from_email='orders@tradifyerp.com',
                recipient_list=[sales_order.customer.email],
                html_message=html_message,
                fail_silently=True
            )
        except Exception as e:
            # Log error but don't fail order
            print(f"Error sending order confirmation: {str(e)}")
    
    @staticmethod
    def _send_shipment_notification(shipment):
        """Send shipment tracking info to customer."""
        try:
            context = {
                'shipment': shipment,
                'tracking_number': shipment.tracking_number,
                'carrier': shipment.carrier_name,
                'expected_delivery': shipment.expected_delivery_date,
            }
            
            html_message = render_to_string(
                'sales/emails/shipment_notification.html',
                context
            )
            
            customer = shipment.sales_order.customer
            send_mail(
                subject=f'Your shipment is on the way - {shipment.shipment_number}',
                message='',
                from_email='shipments@tradifyerp.com',
                recipient_list=[customer.email],
                html_message=html_message,
                fail_silently=True
            )
        except Exception as e:
            print(f"Error sending shipment notification: {str(e)}")
    
    @staticmethod
    def _send_payment_receipt(invoice, payment):
        """Send payment receipt to customer."""
        try:
            context = {
                'invoice': invoice,
                'payment': payment,
                'remaining_balance': invoice.total_amount - payment.amount,
            }
            
            html_message = render_to_string(
                'sales/emails/payment_receipt.html',
                context
            )
            
            send_mail(
                subject=f'Payment Receipt - {invoice.invoice_number}',
                message='',
                from_email='payments@tradifyerp.com',
                recipient_list=[invoice.customer.email],
                html_message=html_message,
                fail_silently=True
            )
        except Exception as e:
            print(f"Error sending receipt: {str(e)}")
    
    @staticmethod
    def _notify_warehouse(sales_order):
        """Send order to warehouse system."""
        # Integration with warehouse management system
        # Could send to physical board or email
        pass
```

---

## Data Synchronization

### 1. Real-time Data Sync

```python
# File: sales/sync_manager.py

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import SalesOrder, Invoice, Quotation


@receiver(post_save, sender=SalesOrder)
def sync_sales_order(sender, instance, created, **kwargs):
    """Sync sales order changes to related modules."""
    
    # Clear analytics cache
    cache_key = f"sales_analytics_{instance.entity_id}"
    cache.delete(cache_key)
    
    # Update CRM opportunity if linked
    if created:
        # Log activity in CRM
        pass


@receiver(post_save, sender=Invoice)
def sync_invoice(sender, instance, created, **kwargs):
    """Sync invoice changes."""
    
    # Update AR aging
    from accounting.models import ARAnalytics
    ARAnalytics.update_for_invoice(instance)


@receiver(post_save, sender=Quotation)
def sync_quotation(sender, instance, created, **kwargs):
    """Sync quotation to CRM and analytics."""
    
    # Update CRM opportunity status
    if instance.opportunity:
        instance.opportunity.quote_status = instance.status
        instance.opportunity.save()


class DataSyncManager:
    """Manage data synchronization across modules."""
    
    @staticmethod
    def sync_all_pending():
        """Sync all pending changes."""
        # Run periodically via Celery
        pass
    
    @staticmethod
    def get_sync_status():
        """Get current sync status."""
        return {
            'last_sync': None,
            'pending_items': 0,
            'errors': [],
            'status': 'OK'
        }
```

---

## Implementation Checklist

### Phase 1: Foundation (Week 1-2)
- [ ] Create all models (Quotation, Pricing, Shipment)
- [ ] Implement pricing engine
- [ ] Create basic forms and views
- [ ] Implement GL integration

### Phase 2: Integrations (Week 3-4)
- [ ] Inventory integration
- [ ] CRM integration
- [ ] Manufacturing integration
- [ ] Shipment tracking

### Phase 3: Workflows (Week 5)
- [ ] Order confirmation workflow
- [ ] Payment workflow
- [ ] Shipment workflow
- [ ] Email notifications

### Phase 4: Testing & Deployment (Week 6)
- [ ] Unit tests
- [ ] Integration tests
- [ ] UAT with stakeholders
- [ ] Production deployment

---

**Version:** 1.0  
**Created:** December 6, 2025  
**Last Updated:** December 6, 2025  
**Status:** Ready for Implementation
