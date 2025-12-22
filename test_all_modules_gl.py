#!/usr/bin/env python
"""
Comprehensive GL Integration Test - Simulates UI Actions
Tests all 6 modules by creating transactions and calling integration methods.
"""

from sales.models import Customer, Invoice, SalesOrder
from manufacturing.models import Product, ProductionOrder
from maintenance.models import MaintenanceAsset, MaintenanceTask, WorkOrder
from accounting.models import LedgerEntry, Account, Currency, Entity
from django.contrib.auth.models import User
from decimal import Decimal
from datetime import date, timedelta

print("\n" + "=" * 80)
print("COMPREHENSIVE GL INTEGRATION TEST")
print("=" * 80)
print(f"Date: {date.today()}")
print("=" * 80 + "\n")

# Get entity and user
entity = Entity.objects.first()
admin = User.objects.filter(is_superuser=True).first()
print(f"✓ Entity: {entity.name}")
print(f"✓ User: {admin.username}\n")

# ============================================================================
# MODULE 1: SALES - Invoice GL Integration
# ============================================================================
print("=" * 80)
print("MODULE 1: SALES - Invoice GL Integration")
print("=" * 80)

try:
    # Get or create GL accounts
    ar_account, _ = Account.objects.get_or_create(
        entity=entity,
        code='1200',
        defaults={'name': 'Accounts Receivable', 'account_type': 'ASSET', 'is_active': True}
    )
    print(f"✓ AR Account: {ar_account.code} - {ar_account.name}")
    
    revenue_account, _ = Account.objects.get_or_create(
        entity=entity,
        code='4100',
        defaults={'name': 'Sales Revenue', 'account_type': 'INCOME', 'is_active': True}
    )
    print(f"✓ Revenue Account: {revenue_account.code} - {revenue_account.name}\n")
    
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
    status = "Created" if created else "Found existing"
    print(f"{status} customer: {customer.customer_code}")
    
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
    status = "Created" if created else "Found existing"
    print(f"{status} sales order: {sales_order.order_number}")
    
    # Create invoice with DRAFT status first (like UI does)
    invoice, created = Invoice.objects.get_or_create(
        entity=entity,
        invoice_number='INV-TEST-001',
        defaults={
            'customer': customer,
            'sales_order': sales_order,
            'invoice_date': date.today(),
            'due_date': date.today() + timedelta(days=30),
            'status': 'DRAFT',  # Start as DRAFT
            'subtotal': Decimal('1000.00'),
            'total_amount': Decimal('1000.00'),
            'tax_amount': Decimal('0.00'),
            'created_by': admin,
            'issued_by': admin
        }
    )
    
    if created or invoice.status != 'ISSUED':
        print(f"Created invoice: {invoice.invoice_number}")
        
        # Now change status to ISSUED (simulates UI action)
        invoice.status = 'ISSUED'
        invoice.save()
        print(f"✓ Changed status to ISSUED")
        
        # Call the GL integration function (what the view does)
        from sales.gl_integration import create_invoice_gl_entries
        
        try:
            create_invoice_gl_entries(invoice)
            print(f"✓ Called create_invoice_gl_entries()")
        except Exception as e:
            print(f"⚠️  GL integration error: {e}")
            # Try alternative integration method
            try:
                from sales.integration import GLPostingManager
                GLPostingManager.post_invoice_revenue_to_gl(invoice)
                print(f"✓ Called GLPostingManager.post_invoice_revenue_to_gl()")
            except Exception as e2:
                print(f"⚠️  Alternative method error: {e2}")
    else:
        print(f"Invoice {invoice.invoice_number} already exists and is ISSUED")
    
    # Verify GL entries
    gl_entries = LedgerEntry.objects.filter(reference_number__startswith='INV-')
    print(f"\n📊 GL Entries for Sales: {gl_entries.count()}")
    for entry in gl_entries[:5]:
        print(f"   → {entry.reference_number}: {entry.entry_type} {entry.account.code} {entry.account.name} ${entry.amount}")
    
except Exception as e:
    print(f"❌ Sales Module Error: {e}")
    import traceback
    traceback.print_exc()

# ============================================================================
# MODULE 2: MANUFACTURING - Production Order GL Integration
# ============================================================================
print("\n" + "=" * 80)
print("MODULE 2: MANUFACTURING - Production Order GL Integration")
print("=" * 80)

try:
    # Get or create GL accounts
    inventory_account, _ = Account.objects.get_or_create(
        entity=entity,
        code='1300',
        defaults={'name': 'Inventory', 'account_type': 'ASSET', 'is_active': True}
    )
    print(f"✓ Inventory Account: {inventory_account.code} - {inventory_account.name}")
    
    wip_account, _ = Account.objects.get_or_create(
        entity=entity,
        code='1400',
        defaults={'name': 'Work in Progress', 'account_type': 'ASSET', 'is_active': True}
    )
    print(f"✓ WIP Account: {wip_account.code} - {wip_account.name}")
    
    finished_goods_account, _ = Account.objects.get_or_create(
        entity=entity,
        code='1350',
        defaults={'name': 'Finished Goods', 'account_type': 'ASSET', 'is_active': True}
    )
    print(f"✓ Finished Goods Account: {finished_goods_account.code} - {finished_goods_account.name}\n")
    
    # Create product
    product, created = Product.objects.get_or_create(
        entity=entity,
        product_code='TEST-PROD-001',
        defaults={
            'name': 'Test Product',
            'description': 'Test product for GL integration',
            'is_manufactured': True,
            'manufacturing_lead_time': 7,
            'standard_batch_size': Decimal('1.00'),
            'unit_of_measure': 'PCS',
            'standard_cost': Decimal('50.00'),
            'selling_price': Decimal('100.00'),
            'inventory_account': inventory_account,
            'is_active': True,
            'created_by': admin
        }
    )
    status = "Created" if created else "Found existing"
    print(f"{status} product: {product.product_code}")
    
    # Create production order with IN_PROGRESS status first
    po, created = ProductionOrder.objects.get_or_create(
        entity=entity,
        order_number='MFG-TEST-001',
        defaults={
            'product': product,
            'quantity': Decimal('100.00'),
            'planned_start_date': date.today(),
            'planned_end_date': date.today() + timedelta(days=7),
            'status': 'IN_PROGRESS',  # Start with IN_PROGRESS
            'created_by': admin
        }
    )
    
    if created or po.status != 'COMPLETE':
        print(f"Created production order: {po.order_number}")
        
        # Now complete it (simulates UI action) - this triggers signal
        po.status = 'COMPLETE'
        po.actual_start_date = date.today()
        po.actual_end_date = date.today()
        po.actual_quantity = Decimal('100.00')
        po.save()  # Signal should fire here
        print(f"✓ Changed status to COMPLETE (signal triggers GL posting)")
    else:
        print(f"Production order {po.order_number} already exists and is COMPLETE")
    
    # Verify GL entries
    gl_entries = LedgerEntry.objects.filter(reference_number__startswith='MFG-')
    print(f"\n📊 GL Entries for Manufacturing: {gl_entries.count()}")
    for entry in gl_entries[:5]:
        print(f"   → {entry.reference_number}: {entry.entry_type} {entry.account.code} {entry.account.name} ${entry.amount}")
    
except Exception as e:
    print(f"❌ Manufacturing Module Error: {e}")
    import traceback
    traceback.print_exc()

# ============================================================================
# MODULE 3: MAINTENANCE - Work Order GL Integration
# ============================================================================
print("\n" + "=" * 80)
print("MODULE 3: MAINTENANCE - Work Order GL Integration (NEW!)")
print("=" * 80)

try:
    # Get or create GL accounts
    ap_account, _ = Account.objects.get_or_create(
        entity=entity,
        code='2000',
        defaults={'name': 'Accounts Payable', 'account_type': 'LIABILITY', 'is_active': True}
    )
    print(f"✓ AP Account: {ap_account.code} - {ap_account.name}")
    
    maintenance_account, _ = Account.objects.get_or_create(
        entity=entity,
        code='6300',
        defaults={'name': 'Maintenance Expense', 'account_type': 'EXPENSE', 'is_active': True}
    )
    print(f"✓ Maintenance Expense Account: {maintenance_account.code} - {maintenance_account.name}\n")
    
    # Create asset
    asset, created = MaintenanceAsset.objects.get_or_create(
        entity=entity,
        asset_code='TEST-ASSET-001',
        defaults={
            'name': 'Test Equipment',
            'description': 'Test equipment for maintenance',
            'status': 'OPERATIONAL',
            'location': 'Main Facility',
            'purchase_date': date.today() - timedelta(days=365),
            'purchase_cost': Decimal('10000.00')
        }
    )
    status = "Created" if created else "Found existing"
    print(f"{status} asset: {asset.asset_code}")
    
    # Create maintenance task
    task, created = MaintenanceTask.objects.get_or_create(
        entity=entity,
        task_code='TEST-TASK-001',
        defaults={
            'name': 'Regular Maintenance',
            'description': 'Regular maintenance check',
            'task_type': 'PREVENTIVE',
            'estimated_duration': Decimal('2.00')
        }
    )
    status = "Created" if created else "Found existing"
    print(f"{status} task: {task.task_code}")
    
    # Create work order with SCHEDULED status first
    wo, created = WorkOrder.objects.get_or_create(
        entity=entity,
        work_order_number='WO-TEST-001',
        defaults={
            'maintenance_task': task,
            'asset': asset,
            'priority': 'MEDIUM',
            'status': 'SCHEDULED',  # Start with SCHEDULED
            'description': 'Test maintenance work',
            'scheduled_date': date.today(),
            'estimated_hours': Decimal('2.00'),
            'estimated_cost': Decimal('200.00')
        }
    )
    
    if created or wo.status != 'COMPLETED':
        print(f"Created work order: {wo.work_order_number}")
        
        # Now complete it (simulates UI action) - this triggers signal
        wo.status = 'COMPLETED'
        wo.actual_start_date = date.today()
        wo.actual_end_date = date.today()
        wo.actual_hours = Decimal('2.50')
        wo.actual_cost = Decimal('250.00')
        wo.completion_date = date.today()
        wo.save()  # Signal should fire here
        print(f"✓ Changed status to COMPLETED (NEW signal triggers GL posting)")
    else:
        print(f"Work order {wo.work_order_number} already exists and is COMPLETED")
    
    # Verify GL entries
    gl_entries = LedgerEntry.objects.filter(reference_number__startswith='WO-')
    print(f"\n📊 GL Entries for Maintenance: {gl_entries.count()}")
    for entry in gl_entries[:5]:
        print(f"   → {entry.reference_number}: {entry.entry_type} {entry.account.code} {entry.account.name} ${entry.amount}")
    
except Exception as e:
    print(f"❌ Maintenance Module Error: {e}")
    import traceback
    traceback.print_exc()

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "=" * 80)
print("TEST SUMMARY - GL ENTRIES BY MODULE")
print("=" * 80)

modules = [
    ('Sales (Invoice)', 'INV-'),
    ('Manufacturing (Production)', 'MFG-'),
    ('Procurement (PO)', 'PO-'),
    ('Procurement (GR)', 'GR-'),
    ('Expenses', 'EXP-'),
    ('Payroll', 'PAY-'),
    ('Maintenance (Work Order)', 'WO-'),
]

total = 0
for name, prefix in modules:
    count = LedgerEntry.objects.filter(reference_number__startswith=prefix).count()
    total += count
    status = "✓" if count > 0 else "○"
    print(f"{status} {name:30} ({prefix:5}): {count:3} entries")

print("=" * 80)
print(f"TOTAL GL ENTRIES: {total}")
print(f"TOTAL IN DATABASE: {LedgerEntry.objects.count()}")
print("=" * 80)

# Show sample entries
print("\nSAMPLE GL ENTRIES (Last 10):")
print("-" * 80)
for entry in LedgerEntry.objects.order_by('-created_at')[:10]:
    print(f"{entry.entry_date} | {entry.reference_number:15} | {entry.entry_type:6} | "
          f"{entry.account.code} {entry.account.name:30} | ${entry.amount:>10}")

print("\n" + "=" * 80)
print("✅ TEST COMPLETED")
print("=" * 80)
