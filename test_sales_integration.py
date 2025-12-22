#!/usr/bin/env python
"""Create test transaction for sales module to test GL integration."""

from sales.models import Customer, Invoice, InvoiceItem, SalesOrder, SalesOrderLine
from accounting.models import LedgerEntry, GLAccount as Account, Currency
from core.models import Entity
from django.contrib.auth.models import User
from decimal import Decimal
from datetime import date, timedelta
import traceback

print("=" * 80)
print("SALES MODULE - Creating Test Invoice")
print("=" * 80)

try:
    # Get entity
    entity = Entity.objects.first()
    print(f"Entity: {entity.name}")
    
    # Get user
    admin = User.objects.filter(is_superuser=True).first()
    print(f"User: {admin.username}\n")
    
    # Get or create GL accounts
    ar_account, created = Account.objects.get_or_create(
        entity=entity,
        code='1200',
        defaults={'name': 'Accounts Receivable', 'account_type': 'ASSET', 'is_active': True}
    )
    if created:
        print(f"✅ Created GL account: {ar_account.code} - {ar_account.name}")
    
    revenue_account, created = Account.objects.get_or_create(
        entity=entity,
        code='4100',
        defaults={'name': 'Sales Revenue', 'account_type': 'INCOME', 'is_active': True}
    )
    if created:
        print(f"✅ Created GL account: {revenue_account.code} - {revenue_account.name}\n")
    
    # Create customer
    customer, created = Customer.objects.get_or_create(
        entity=entity,
        customer_code='TEST-CUST-001',
        defaults={
            'customer_name': 'Test Customer Inc',
            'email': 'testcust@example.com',
            'phone': '555-0001',
            'customer_type': 'BUSINESS',
            'credit_limit': Decimal('10000.00'),
            'is_tax_exempt': False,
            'status': 'ACTIVE'
        }
    )
    if created:
        print(f"✅ Created customer: {customer.customer_code} - {customer.customer_name}")
    else:
        print(f"ℹ️  Using existing customer: {customer.customer_code}")
    
    # Create sales order
    sales_order, created = SalesOrder.objects.get_or_create(
        entity=entity,
        order_number='SO-TEST-001',
        defaults={
            'customer': customer,
            'order_date': date.today(),
            'delivery_date': date.today() + timedelta(days=7),
            'status': 'CONFIRMED',
            'total_amount': Decimal('1000.00'),
            'created_by': admin
        }
    )
    if created:
        print(f"✅ Created sales order: {sales_order.order_number}")
    else:
        print(f"ℹ️  Using existing sales order: {sales_order.order_number}")
    
    # Create invoice
    invoice, created = Invoice.objects.get_or_create(
        entity=entity,
        invoice_number='INV-TEST-001',
        defaults={
            'customer': customer,
            'sales_order': sales_order,
            'invoice_date': date.today(),
            'due_date': date.today() + timedelta(days=30),
            'status': 'ISSUED',  # This should trigger GL posting
            'subtotal': Decimal('1000.00'),
            'total_amount': Decimal('1000.00'),
            'created_by': admin
        }
    )
    
    if created:
        # Create invoice item
        InvoiceItem.objects.create(
            invoice=invoice,
            description='Test Product',
            quantity=Decimal('10.00'),
            unit_price=Decimal('100.00'),
            amount=Decimal('1000.00')
        )
        print(f"✅ Created invoice: {invoice.invoice_number}")
        print(f"   Customer: {customer.customer_name}")
        print(f"   Amount: ${invoice.total_amount}")
        print(f"   Status: {invoice.status}")
        print(f"   Date: {invoice.invoice_date}")
    else:
        print(f"ℹ️  Invoice already exists: {invoice.invoice_number}")
    
    # Check for GL entries
    print("\n" + "-" * 80)
    gl_entries = LedgerEntry.objects.filter(reference_number__startswith='INV-')
    print(f"GL Entries with 'INV-' prefix: {gl_entries.count()}")
    
    if gl_entries.exists():
        for entry in gl_entries[:5]:
            print(f"  - {entry.reference_number}: {entry.entry_type} {entry.account.code} ${entry.amount}")
    else:
        print("  ⚠️  No GL entries found - sales integration may not be working")
        print("\n  Checking if GLPostingManager was called...")
        print("  (Requires debugging sales/integration.py signals)")
    
    print("=" * 80)
    print("✅ Sales test transaction completed")
    print("=" * 80)
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    traceback.print_exc()
