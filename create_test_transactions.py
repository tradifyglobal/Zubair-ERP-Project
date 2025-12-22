"""
Create Test Transactions for All Modules
Verifies GL integration by creating real transactions
"""

import paramiko
from datetime import datetime
import time

def run_cmd(ssh, cmd, timeout=90):
    """Execute command and return output"""
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    return stdout.read().decode('utf-8'), stderr.read().decode('utf-8')

def upload_file(ssh, local_content, remote_path):
    """Upload file content to remote server"""
    sftp = ssh.open_sftp()
    with sftp.file(remote_path, 'w') as f:
        f.write(local_content)
    sftp.close()

def main():
    host = '192.168.20.10'
    username = 'zubair'
    password = 'erp'
    
    print("="*80)
    print("CREATING TEST TRANSACTIONS FOR ALL MODULES")
    print("="*80)
    print(f"Server: {host}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    print()
    
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, username=username, password=password)
        print("✅ Connected to server\n")
        
        # Test script for all modules
        test_script = """
import os, sys, django
sys.path.insert(0, '/var/www/tradifyerp')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
from datetime import datetime, timedelta

from accounting.models import Entity, Account, LedgerEntry, Vendor
from sales.models import Invoice, Customer
from manufacturing.models import ProductionOrder, Product, BillOfMaterials
from procurement.models import PurchaseOrder, GoodsReceipt
from expenses.models import EmployeeExpense, EmployeeExpenseReport, ExpenseCategory
from hr.models import Employee, Position, Department
from maintenance.models import WorkOrder, MaintenanceAsset, MaintenanceCost

print("="*80)
print("CREATING TEST TRANSACTIONS")
print("="*80)

entity = Entity.objects.first()
user = User.objects.first()

if not entity or not user:
    print("ERROR: No entity or user found")
    sys.exit(1)

print(f"Entity: {entity.name}")
print(f"User: {user.username}")
print()

# ============================================================================
# 1. SALES MODULE - Create Test Invoice
# ============================================================================
print("1. SALES MODULE - Creating Test Invoice")
print("-"*80)

try:
    # Get/create required accounts
    ar_account, _ = Account.objects.get_or_create(
        entity=entity,
        account_number='1200',
        defaults={
            'name': 'Accounts Receivable',
            'account_type': 'ASSET',
            'is_active': True,
            'currency': entity.company_currency,
            'description': 'Customer receivables'
        }
    )
    
    revenue_account, _ = Account.objects.get_or_create(
        entity=entity,
        account_number='4100',
        defaults={
            'name': 'Sales Revenue',
            'account_type': 'INCOME',
            'is_active': True,
            'currency': entity.company_currency,
            'description': 'Sales revenue'
        }
    )
    
    # Get/create customer
    customer, _ = Customer.objects.get_or_create(
        entity=entity,
        email='testcustomer@example.com',
        defaults={
            'name': 'Test Customer Ltd',
            'phone': '555-0001',
            'address': 'Test Address',
            'city': 'Test City'
        }
    )
    
    # Create invoice
    invoice = Invoice.objects.create(
        entity=entity,
        customer=customer,
        invoice_number=f'TEST-INV-{datetime.now().strftime("%Y%m%d%H%M%S")}',
        invoice_date=timezone.now().date(),
        due_date=timezone.now().date() + timedelta(days=30),
        subtotal=Decimal('1000.00'),
        tax_amount=Decimal('100.00'),
        total_amount=Decimal('1100.00'),
        status='ISSUED',
        issued_by=user
    )
    
    print(f"✅ Created Invoice: {invoice.invoice_number}")
    
    # Check GL entries
    gl_entries = LedgerEntry.objects.filter(reference_number__contains=str(invoice.id))
    print(f"   GL Entries Created: {gl_entries.count()}")
    for entry in gl_entries:
        print(f"   - {entry.entry_type}: {entry.account.name} = ${entry.amount}")
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

print()

# ============================================================================
# 2. MANUFACTURING MODULE - Create Production Order
# ============================================================================
print("2. MANUFACTURING MODULE - Creating Production Order")
print("-"*80)

try:
    # Get/create required accounts
    inventory_account, _ = Account.objects.get_or_create(
        entity=entity,
        account_number='1300',
        defaults={
            'name': 'Finished Goods Inventory',
            'account_type': 'CURRENT_ASSET',
            'is_active': True,
            'currency': entity.company_currency
        }
    )
    
    wip_account, _ = Account.objects.get_or_create(
        entity=entity,
        account_number='1400',
        defaults={
            'name': 'Work in Process',
            'account_type': 'CURRENT_ASSET',
            'is_active': True,
            'currency': entity.company_currency
        }
    )
    
    # Get/create product
    product, created = Product.objects.get_or_create(
        entity=entity,
        product_code=f'TEST-PROD-{datetime.now().strftime("%H%M%S")}',
        defaults={
            'name': 'Test Product',
            'description': 'Test product for GL integration',
            'unit_of_measure': 'PCS',
            'inventory_account': inventory_account
        }
    )
    
    # Create BOM if doesn't exist
    if not hasattr(product, 'bom') or not product.bom:
        bom = BillOfMaterials.objects.create(
            entity=entity,
            product=product,
            bom_number=f'BOM-{product.product_code}',
            version=1,
            is_active=True,
            status='APPROVED'
        )
    else:
        bom = product.bom
    
    # Create production order
    po = ProductionOrder.objects.create(
        entity=entity,
        po_number=f'TEST-MFG-{datetime.now().strftime("%Y%m%d%H%M%S")}',
        product=product,
        bom=bom,
        quantity_planned=Decimal('10.00'),
        quantity_completed=Decimal('10.00'),
        status='COMPLETE',
        start_date=timezone.now().date(),
        due_date=timezone.now().date(),
        completion_date=timezone.now().date(),
        estimated_material_cost=Decimal('500.00'),
        estimated_labor_cost=Decimal('200.00'),
        total_estimated_cost=Decimal('700.00'),
        actual_material_cost=Decimal('520.00'),
        actual_labor_cost=Decimal('210.00'),
        total_actual_cost=Decimal('730.00'),
        created_by=user
    )
    
    print(f"✅ Created Production Order: {po.po_number}")
    
    # Check GL entries
    time.sleep(1)  # Give signal time to process
    gl_entries = LedgerEntry.objects.filter(reference_number=f'MFG-{po.po_number}')
    print(f"   GL Entries Created: {gl_entries.count()}")
    for entry in gl_entries:
        print(f"   - {entry.entry_type}: {entry.account.name} = ${entry.amount}")
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

print()

# ============================================================================
# 3. PROCUREMENT MODULE - Create Purchase Order & Goods Receipt
# ============================================================================
print("3. PROCUREMENT MODULE - Creating PO & Goods Receipt")
print("-"*80)

try:
    # Ensure inventory and AP accounts exist
    inventory_account, _ = Account.objects.get_or_create(
        entity=entity,
        account_number='1300',
        defaults={
            'name': 'Inventory',
            'account_type': 'ASSET',
            'is_active': True,
            'currency': entity.company_currency
        }
    )
    
    ap_account, _ = Account.objects.get_or_create(
        entity=entity,
        account_number='2000',
        defaults={
            'name': 'Accounts Payable',
            'account_type': 'LIABILITY',
            'is_active': True,
            'currency': entity.company_currency
        }
    )
    
    # Get/create vendor
    vendor, _ = Vendor.objects.get_or_create(
        entity=entity,
        email='testvendor@example.com',
        defaults={
            'name': 'Test Vendor Inc',
            'phone': '555-0002',
            'address': 'Vendor Address'
        }
    )
    
    # Create PO
    po = PurchaseOrder.objects.create(
        entity=entity,
        vendor=vendor,
        po_number=f'TEST-PO-{datetime.now().strftime("%Y%m%d%H%M%S")}',
        total_amount=Decimal('5000.00'),
        subtotal=Decimal('4500.00'),
        tax_amount=Decimal('500.00'),
        status='SENT',
        is_approved=True,
        approved_by=user,
        created_by=user
    )
    
    print(f"✅ Created Purchase Order: {po.po_number}")
    
    # Create Goods Receipt
    gr = GoodsReceipt.objects.create(
        entity=entity,
        purchase_order=po,
        receipt_number=f'TEST-GR-{datetime.now().strftime("%Y%m%d%H%M%S")}',
        receipt_date=timezone.now().date(),
        status='RECEIVED',
        received_by=user
    )
    
    print(f"✅ Created Goods Receipt: {gr.receipt_number}")
    
    # Trigger GL posting manually
    from procurement.gl_integration import create_gr_gl_entries
    result = create_gr_gl_entries(gr)
    print(f"   GL Posting Result: {result}")
    
    # Check GL entries
    gl_entries = LedgerEntry.objects.filter(reference_number__contains=str(po.id))
    gr_entries = LedgerEntry.objects.filter(reference_number__contains=str(gr.id))
    total = gl_entries.count() + gr_entries.count()
    print(f"   GL Entries Created: {total}")
    for entry in list(gl_entries) + list(gr_entries):
        print(f"   - {entry.entry_type}: {entry.account.name} = ${entry.amount}")
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

print()

# ============================================================================
# 4. EXPENSES MODULE - Create Employee Expense
# ============================================================================
print("4. EXPENSES MODULE - Creating Employee Expense")
print("-"*80)

try:
    # Get/create expense account
    expense_account, _ = Account.objects.get_or_create(
        entity=entity,
        account_number='6100',
        defaults={
            'name': 'Travel Expense',
            'account_type': 'EXPENSE',
            'is_active': True,
            'currency': entity.company_currency
        }
    )
    
    # Get/create category
    category, _ = ExpenseCategory.objects.get_or_create(
        entity=entity,
        code='TRAVEL',
        defaults={
            'name': 'Travel & Transportation',
            'expense_account': expense_account,
            'is_active': True
        }
    )
    
    # Get active employee
    employee = Employee.objects.filter(entity=entity, status='ACTIVE').first()
    if not employee:
        # Create test employee
        dept, _ = Department.objects.get_or_create(
            entity=entity,
            code='TEST',
            defaults={'name': 'Test Department'}
        )
        
        pos, _ = Position.objects.get_or_create(
            entity=entity,
            title='Test Employee',
            defaults={'department': dept}
        )
        
        employee = Employee.objects.create(
            entity=entity,
            employee_number=f'EMP-TEST-{datetime.now().strftime("%H%M%S")}',
            first_name='Test',
            last_name='Employee',
            email='test@employee.com',
            position=pos,
            department=dept,
            hire_date=timezone.now().date(),
            status='ACTIVE'
        )
    
    # Create expense report
    report = EmployeeExpenseReport.objects.create(
        entity=entity,
        employee=employee,
        report_number=f'TEST-EXP-{datetime.now().strftime("%Y%m%d%H%M%S")}',
        period_start=timezone.now().date(),
        period_end=timezone.now().date(),
        status='APPROVED'
    )
    
    print(f"✅ Created Expense Report: {report.report_number}")
    
    # Create expense
    expense = EmployeeExpense.objects.create(
        report=report,
        category=category,
        expense_date=timezone.now().date(),
        description='Test travel expense - taxi fare',
        amount=Decimal('150.00'),
        status='APPROVED'
    )
    
    print(f"✅ Created Expense: ${expense.amount}")
    
    # Post to GL
    result = expense.post_to_gl()
    print(f"   GL Posting Result: {result}")
    
    # Check GL entries
    gl_entries = LedgerEntry.objects.filter(reference_number=f'EXP-{report.id}-{expense.id}')
    print(f"   GL Entries Created: {gl_entries.count()}")
    for entry in gl_entries:
        print(f"   - {entry.entry_type}: {entry.account.name} = ${entry.amount}")
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

print()

# ============================================================================
# 5. MAINTENANCE MODULE - Create Work Order
# ============================================================================
print("5. MAINTENANCE MODULE - Creating Work Order")
print("-"*80)

try:
    # Get/create maintenance expense account
    maint_account, _ = Account.objects.get_or_create(
        entity=entity,
        account_number='6300',
        defaults={
            'name': 'Maintenance Expense',
            'account_type': 'EXPENSE',
            'is_active': True,
            'currency': entity.company_currency
        }
    )
    
    # Get/create asset
    asset, _ = MaintenanceAsset.objects.get_or_create(
        entity=entity,
        asset_code=f'TEST-ASSET-{datetime.now().strftime("%H%M%S")}',
        defaults={
            'asset_name': 'Test Equipment',
            'asset_type': 'EQUIPMENT',
            'location': 'Test Floor',
            'purchase_date': timezone.now().date(),
            'acquisition_cost': Decimal('10000.00'),
            'status': 'OPERATIONAL'
        }
    )
    
    # Create work order
    wo = WorkOrder.objects.create(
        entity=entity,
        work_order_number=f'TEST-WO-{datetime.now().strftime("%Y%m%d%H%M%S")}',
        asset=asset,
        priority='MEDIUM',
        status='COMPLETED',
        assigned_to=user,
        description='Test preventive maintenance',
        scheduled_date=timezone.now().date(),
        completion_date=timezone.now().date(),
        estimated_hours=Decimal('4.00'),
        actual_hours=Decimal('4.50'),
        estimated_cost=Decimal('300.00'),
        actual_cost=Decimal('325.00')
    )
    
    print(f"✅ Created Work Order: {wo.work_order_number}")
    
    # Add maintenance costs
    labor_cost = MaintenanceCost.objects.create(
        entity=entity,
        work_order=wo,
        cost_type='LABOR',
        description='Technician labor - 4.5 hours',
        amount=Decimal('225.00'),
        cost_date=timezone.now().date()
    )
    
    parts_cost = MaintenanceCost.objects.create(
        entity=entity,
        work_order=wo,
        cost_type='PARTS',
        description='Replacement parts',
        amount=Decimal('100.00'),
        cost_date=timezone.now().date()
    )
    
    print(f"✅ Added Costs: Labor=${labor_cost.amount}, Parts=${parts_cost.amount}")
    
    # Check GL entries (should be auto-created by signal)
    time.sleep(1)  # Give signal time to process
    gl_entries = LedgerEntry.objects.filter(reference_number=f'WO-{wo.id}')
    print(f"   GL Entries Created: {gl_entries.count()}")
    for entry in gl_entries:
        print(f"   - {entry.entry_type}: {entry.account.name} = ${entry.amount}")
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

print()
print("="*80)
print("TEST TRANSACTIONS SUMMARY")
print("="*80)

# Final count
inv_count = LedgerEntry.objects.filter(reference_number__startswith='INV-').count()
mfg_count = LedgerEntry.objects.filter(reference_number__startswith='MFG-').count()
po_count = LedgerEntry.objects.filter(reference_number__startswith='PO-').count()
gr_count = LedgerEntry.objects.filter(reference_number__startswith='GR-').count()
exp_count = LedgerEntry.objects.filter(reference_number__startswith='EXP-').count()
wo_count = LedgerEntry.objects.filter(reference_number__startswith='WO-').count()

print(f"Sales (INV-):          {inv_count} entries")
print(f"Manufacturing (MFG-):  {mfg_count} entries")
print(f"Procurement (PO-/GR-): {po_count + gr_count} entries")
print(f"Expenses (EXP-):       {exp_count} entries")
print(f"Maintenance (WO-):     {wo_count} entries")
print("="*80)
"""
        
        # Upload and execute test script
        print("📝 Uploading test transaction script...")
        upload_file(ssh, test_script, '/tmp/create_test_transactions.py')
        
        print("🧪 Creating test transactions...\n")
        print("="*80)
        
        output, error = run_cmd(ssh, '/var/www/tradifyerp/venv/bin/python /tmp/create_test_transactions.py')
        print(output)
        
        if error and ('Traceback' in error or 'Error' in error):
            print("\n⚠️ Errors:")
            print(error)
        
        # Cleanup
        run_cmd(ssh, 'rm /tmp/create_test_transactions.py')
        
        ssh.close()
        print("\n✅ Test completed")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
