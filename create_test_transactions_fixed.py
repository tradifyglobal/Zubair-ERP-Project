#!/usr/bin/env python
"""Create test transactions for all modules to verify GL integration."""

import sys
import os

# SSH connection details
SERVER = "192.168.2.69"
USER = "zubair"
DJANGO_PATH = "/var/www/tradifyerp"

import paramiko
from datetime import datetime

def create_test_transactions():
    """Connect and create test transactions."""
    print("=" * 80)
    print("CREATING TEST TRANSACTIONS FOR ALL MODULES")
    print("=" * 80)
    print(f"Server: {SERVER}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80 + "\n")
    
    # Create SSH client
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        # Connect
        ssh.connect(SERVER, username=USER, password="erp")
        print("✅ Connected to server\n")
        
        # Upload test script
        script_content = '''
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tradifyerp.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import Entity
from sales.models import Customer, Invoice, InvoiceItem, SalesOrder, SalesOrderLine
from manufacturing.models import Product, ProductionOrder
from accounting.models import Vendor, Currency, GLAccount
from procurement.models import PurchaseOrder, PurchaseOrderItem, GoodsReceipt
from expenses.models import EmployeeExpense, ExpenseCategory
from maintenance.models import WorkOrder, MaintenanceTask, Asset
from hr.models import Employee
from accounting.models import LedgerEntry
from decimal import Decimal
from datetime import date, timedelta

print("=" * 80)
print("CREATING TEST TRANSACTIONS")
print("=" * 80)

# Get entity and user
entity = Entity.objects.filter(name="Internal").first()
if not entity:
    entity = Entity.objects.first()
print(f"Entity: {entity.name}")

admin = User.objects.filter(username="admin").first()
if not admin:
    admin = User.objects.first()
print(f"User: {admin.username}\\n")

# Get or create GL accounts
def get_or_create_account(code, name, account_type):
    account, created = GLAccount.objects.get_or_create(
        entity=entity,
        code=code,
        defaults={
            'name': name,
            'account_type': account_type,
            'is_active': True
        }
    )
    return account

ar_account = get_or_create_account('1200', 'Accounts Receivable', 'ASSET')
revenue_account = get_or_create_account('4100', 'Sales Revenue', 'INCOME')
ap_account = get_or_create_account('2000', 'Accounts Payable', 'LIABILITY')
inventory_account = get_or_create_account('1300', 'Inventory', 'ASSET')
wip_account = get_or_create_account('1400', 'Work in Progress', 'ASSET')
salary_account = get_or_create_account('6000', 'Salary Expense', 'EXPENSE')
travel_account = get_or_create_account('6100', 'Travel Expense', 'EXPENSE')
maintenance_account = get_or_create_account('6300', 'Maintenance Expense', 'EXPENSE')
finished_goods_account = get_or_create_account('1350', 'Finished Goods', 'ASSET')

# Get or create currency
currency, _ = Currency.objects.get_or_create(
    code='USD',
    defaults={'name': 'US Dollar', 'symbol': '$', 'is_active': True}
)

print("1. SALES MODULE - Creating Test Invoice")
print("-" * 80)
try:
    # Create customer
    customer, _ = Customer.objects.get_or_create(
        entity=entity,
        customer_code='TEST-CUST-001',
        defaults={
            'customer_name': 'Test Customer Inc',
            'email': 'testcustomer@example.com',
            'phone': '555-0001',
            'customer_type': 'BUSINESS',
            'credit_limit': Decimal('10000.00'),
            'is_tax_exempt': False,
            'status': 'ACTIVE'
        }
    )
    
    # Create sales order first
    sales_order, _ = SalesOrder.objects.get_or_create(
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
    
    # Create invoice
    invoice, created = Invoice.objects.get_or_create(
        entity=entity,
        invoice_number='INV-TEST-001',
        defaults={
            'customer': customer,
            'sales_order': sales_order,
            'invoice_date': date.today(),
            'due_date': date.today() + timedelta(days=30),
            'status': 'ISSUED',
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
        print(f"   Amount: ${invoice.total_amount}")
        print(f"   Status: {invoice.status}")
    else:
        print(f"ℹ️  Invoice already exists: {invoice.invoice_number}")
        
except Exception as e:
    print(f"❌ ERROR: {e}")

print("\\n2. MANUFACTURING MODULE - Creating Production Order")
print("-" * 80)
try:
    # Create product
    product, created = Product.objects.get_or_create(
        entity=entity,
        product_code='TEST-PROD-001',
        defaults={
            'name': 'Test Product',
            'description': 'Test product for GL integration',
            'category': None,
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
    
    # Create production order
    po, created = ProductionOrder.objects.get_or_create(
        entity=entity,
        order_number='MFG-TEST-001',
        defaults={
            'product': product,
            'quantity': Decimal('100.00'),
            'planned_start_date': date.today(),
            'planned_end_date': date.today() + timedelta(days=7),
            'status': 'COMPLETE',
            'actual_start_date': date.today(),
            'actual_end_date': date.today(),
            'actual_quantity': Decimal('100.00'),
            'created_by': admin
        }
    )
    
    if created:
        print(f"✅ Created production order: {po.order_number}")
        print(f"   Product: {product.name}")
        print(f"   Quantity: {po.quantity}")
        print(f"   Status: {po.status}")
    else:
        print(f"ℹ️  Production order already exists: {po.order_number}")
        
except Exception as e:
    print(f"❌ ERROR: {e}")

print("\\n3. PROCUREMENT MODULE - Creating PO & Goods Receipt")
print("-" * 80)
try:
    # Create vendor
    vendor, created = Vendor.objects.get_or_create(
        entity=entity,
        vendor_code='TEST-VEND-001',
        defaults={
            'name': 'Test Vendor Inc',
            'email': 'testvendor@example.com',
            'phone': '555-0002',
            'address': 'Vendor Address',
            'currency': currency,
            'is_active': True
        }
    )
    
    # Create purchase order
    purchase_order, created = PurchaseOrder.objects.get_or_create(
        entity=entity,
        po_number='PO-TEST-001',
        defaults={
            'vendor': vendor,
            'order_date': date.today(),
            'expected_delivery_date': date.today() + timedelta(days=7),
            'status': 'APPROVED',
            'total_amount': Decimal('500.00'),
            'created_by': admin
        }
    )
    
    # Create PO item if new
    if created:
        PurchaseOrderItem.objects.create(
            purchase_order=purchase_order,
            product=product,
            quantity=Decimal('50.00'),
            unit_price=Decimal('10.00'),
            total=Decimal('500.00')
        )
    
    # Create goods receipt
    gr, created = GoodsReceipt.objects.get_or_create(
        entity=entity,
        gr_number='GR-TEST-001',
        defaults={
            'purchase_order': purchase_order,
            'received_date': date.today(),
            'status': 'COMPLETED',
            'created_by': admin
        }
    )
    
    if created:
        print(f"✅ Created PO: {purchase_order.po_number}")
        print(f"   Vendor: {vendor.name}")
        print(f"   Amount: ${purchase_order.total_amount}")
        print(f"✅ Created GR: {gr.gr_number}")
    else:
        print(f"ℹ️  PO/GR already exists: {purchase_order.po_number}/{gr.gr_number}")
        
except Exception as e:
    print(f"❌ ERROR: {e}")

print("\\n4. EXPENSES MODULE - Creating Employee Expense")
print("-" * 80)
try:
    # Get employee
    employee = Employee.objects.filter(entity=entity).first()
    if not employee:
        print("⚠️  No employees found - skipping expense test")
    else:
        # Create expense category
        category, _ = ExpenseCategory.objects.get_or_create(
            entity=entity,
            name='Travel',
            defaults={
                'category_type': 'TRAVEL',
                'description': 'Travel expenses',
                'expense_account': travel_account,
                'requires_receipt': True,
                'requires_approval': True,
                'is_active': True
            }
        )
        
        # Create expense
        expense, created = EmployeeExpense.objects.get_or_create(
            entity=entity,
            employee=employee,
            expense_date=date.today(),
            category=category,
            defaults={
                'description': 'Test travel expense',
                'amount': Decimal('250.00'),
                'status': 'APPROVED',
                'is_billable': False
            }
        )
        
        if created:
            # Post to GL
            expense.post_to_gl()
            print(f"✅ Created expense for employee: {employee.user.username}")
            print(f"   Category: {category.name}")
            print(f"   Amount: ${expense.amount}")
            print(f"   Status: {expense.status}")
            print(f"   Posted to GL: Yes")
        else:
            print(f"ℹ️  Expense already exists for {employee.user.username}")
        
except Exception as e:
    print(f"❌ ERROR: {e}")

print("\\n5. MAINTENANCE MODULE - Creating Work Order")
print("-" * 80)
try:
    # Get or create asset
    asset, _ = Asset.objects.get_or_create(
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
    
    # Get or create maintenance task
    task, _ = MaintenanceTask.objects.get_or_create(
        entity=entity,
        task_code='TEST-TASK-001',
        defaults={
            'name': 'Regular Maintenance',
            'description': 'Regular maintenance check',
            'task_type': 'PREVENTIVE',
            'estimated_duration': Decimal('2.00')
        }
    )
    
    # Create work order
    wo, created = WorkOrder.objects.get_or_create(
        entity=entity,
        work_order_number='WO-TEST-001',
        defaults={
            'maintenance_task': task,
            'asset': asset,
            'priority': 'MEDIUM',
            'status': 'COMPLETED',
            'description': 'Test maintenance work',
            'scheduled_date': date.today(),
            'actual_start_date': date.today(),
            'actual_end_date': date.today(),
            'estimated_hours': Decimal('2.00'),
            'actual_hours': Decimal('2.50'),
            'estimated_cost': Decimal('200.00'),
            'actual_cost': Decimal('250.00'),
            'completion_date': date.today()
        }
    )
    
    if created:
        print(f"✅ Created work order: {wo.work_order_number}")
        print(f"   Asset: {asset.name}")
        print(f"   Task: {task.name}")
        print(f"   Actual cost: ${wo.actual_cost}")
        print(f"   Status: {wo.status}")
    else:
        print(f"ℹ️  Work order already exists: {wo.work_order_number}")
        
except Exception as e:
    print(f"❌ ERROR: {e}")

# Check GL entries created
print("\\n" + "=" * 80)
print("TEST TRANSACTIONS SUMMARY")
print("=" * 80)

def count_entries(prefix):
    return LedgerEntry.objects.filter(reference__startswith=prefix).count()

print(f"Sales (INV-):          {count_entries('INV-')} entries")
print(f"Manufacturing (MFG-):  {count_entries('MFG-')} entries")
print(f"Procurement (PO-/GR-): {count_entries('PO-') + count_entries('GR-')} entries")
print(f"Expenses (EXP-):       {count_entries('EXP-')} entries")
print(f"Maintenance (WO-):     {count_entries('WO-')} entries")

print("=" * 80)
'''
        
        # Write script to temp file
        sftp = ssh.open_sftp()
        with sftp.open('/tmp/create_test_transactions.py', 'w') as f:
            f.write(script_content)
        sftp.close()
        
        print("📝 Uploading test transaction script...")
        
        # Execute script
        print("🧪 Creating test transactions...\n")
        print("=" * 80)
        cmd = f'cd {DJANGO_PATH} && source venv/bin/activate && python /tmp/create_test_transactions.py'
        stdin, stdout, stderr = ssh.exec_command(cmd)
        
        output = stdout.read().decode()
        error = stderr.read().decode()
        
        if output:
            print(output)
        
        if error:
            print("\n⚠️ Errors:")
            print(error)
        
        print("\n✅ Test completed")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        ssh.close()

if __name__ == "__main__":
    create_test_transactions()
