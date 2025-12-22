"""
Test Module → Accounting Integration
Creates test transactions in each module and verifies GL posting
"""

import paramiko
import sys
from datetime import datetime

def run_remote_command(ssh, command):
    """Execute command on remote server and return output"""
    stdin, stdout, stderr = ssh.exec_command(command)
    output = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')
    return output, error

def main():
    # Server credentials
    host = '192.168.20.10'
    username = 'zubair'
    password = 'erp'
    
    print(f"🔍 Testing Module → Accounting Integration")
    print(f"=" * 80)
    print(f"Server: {host}")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"=" * 80)
    
    try:
        # Connect to server
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        print(f"\n📡 Connecting to {host}...")
        ssh.connect(host, username=username, password=password)
        print(f"✅ Connected successfully")
        
        # Create test script on server
        test_script = '''
import os
import sys
import django

# Setup Django
sys.path.insert(0, '/var/www/tradifyerp')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tradifyerp.settings')
django.setup()

from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
from datetime import datetime, timedelta

from accounting.models import Entity, Account, LedgerEntry
from sales.models import Invoice, Customer
from manufacturing.models import ProductionOrder, Product
from procurement.models import PurchaseOrder, GoodsReceipt
from expenses.models import EmployeeExpense, EmployeeExpenseReport, ExpenseCategory
from hr.models import Payroll, PayrollRecord, Employee, Position, Department
from maintenance.models import WorkOrder, MaintenanceAsset

print("=" * 80)
print("MODULE → ACCOUNTING INTEGRATION TEST")
print("=" * 80)

# Get test entity and user
try:
    entity = Entity.objects.first()
    user = User.objects.first()
    if not entity or not user:
        print("❌ ERROR: No entity or user found")
        sys.exit(1)
    print(f"✓ Using Entity: {entity.name}")
    print(f"✓ Using User: {user.username}")
except Exception as e:
    print(f"❌ ERROR getting entity/user: {e}")
    sys.exit(1)

print()

# ============================================================================
# TEST 1: SALES MODULE
# ============================================================================
print("1️⃣  TESTING SALES MODULE")
print("-" * 80)

try:
    # Count existing entries
    before_count = LedgerEntry.objects.filter(
        reference_number__startswith='INV-'
    ).count()
    print(f"   Existing INV entries: {before_count}")
    
    # Check if customer exists
    customer = Customer.objects.filter(entity=entity).first()
    if not customer:
        print("   ⚠️  No customer found - creating test customer")
        customer = Customer.objects.create(
            entity=entity,
            name="Test Customer",
            email="test@customer.com",
            phone="1234567890"
        )
    
    # Check required GL accounts
    ar_account = Account.objects.filter(
        entity=entity,
        account_type='ASSET',
        name__icontains='receivable'
    ).first()
    
    revenue_account = Account.objects.filter(
        entity=entity,
        account_type='INCOME',
        name__icontains='sales'
    ).first()
    
    if not ar_account or not revenue_account:
        print(f"   ⚠️  Missing GL accounts:")
        print(f"      AR Account: {'Found' if ar_account else 'NOT FOUND'}")
        print(f"      Revenue Account: {'Found' if revenue_account else 'NOT FOUND'}")
        print(f"   ❌ SKIPPED: Cannot test without GL accounts")
    else:
        # Create test invoice
        invoice = Invoice.objects.create(
            entity=entity,
            customer=customer,
            invoice_number=f"TEST-INV-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            invoice_date=timezone.now().date(),
            due_date=timezone.now().date() + timedelta(days=30),
            subtotal=Decimal('1000.00'),
            tax_amount=Decimal('100.00'),
            total_amount=Decimal('1100.00'),
            status='ISSUED',
            issued_by=user
        )
        print(f"   ✓ Created Invoice: {invoice.invoice_number}")
        
        # Check if GL entries were created
        after_count = LedgerEntry.objects.filter(
            reference_number__startswith='INV-'
        ).count()
        
        # Try to find entries for this specific invoice
        invoice_entries = LedgerEntry.objects.filter(
            reference_number__contains=str(invoice.id)
        )
        
        if invoice_entries.exists():
            print(f"   ✅ GL INTEGRATION WORKING")
            print(f"      Created {invoice_entries.count()} ledger entries")
            for entry in invoice_entries:
                print(f"      - {entry.entry_type}: {entry.account.name} = ${entry.amount}")
        else:
            print(f"   ⚠️  GL entries NOT found for invoice ID {invoice.id}")
            print(f"      Total INV entries before: {before_count}")
            print(f"      Total INV entries after: {after_count}")
            if after_count > before_count:
                print(f"      ✓ New entries created: {after_count - before_count}")
            else:
                print(f"      ❌ NO new GL entries created")
                
except Exception as e:
    print(f"   ❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

print()

# ============================================================================
# TEST 2: MANUFACTURING MODULE
# ============================================================================
print("2️⃣  TESTING MANUFACTURING MODULE")
print("-" * 80)

try:
    from accounting.models import JournalEntry
    
    before_count = JournalEntry.objects.filter(
        reference__startswith='MFG-'
    ).count()
    print(f"   Existing MFG entries: {before_count}")
    
    # Check if product exists
    product = Product.objects.filter(entity=entity).first()
    if not product:
        print("   ⚠️  No product found - creating test product")
        
        # Check for inventory account
        inv_account = Account.objects.filter(
            entity=entity,
            account_type='ASSET'
        ).first()
        
        if inv_account:
            product = Product.objects.create(
                entity=entity,
                product_code=f"TEST-PROD-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                name="Test Product",
                description="Test product for integration",
                unit_of_measure="PCS",
                inventory_account=inv_account
            )
        else:
            print("   ❌ SKIPPED: No inventory account found")
            product = None
    
    if product:
        # Create production order
        po = ProductionOrder.objects.create(
            entity=entity,
            po_number=f"TEST-MFG-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            product=product,
            quantity_planned=Decimal('10.00'),
            quantity_completed=Decimal('10.00'),
            status='COMPLETE',  # This should trigger GL posting
            start_date=timezone.now().date(),
            due_date=timezone.now().date(),
            actual_material_cost=Decimal('500.00'),
            actual_labor_cost=Decimal('200.00'),
            total_actual_cost=Decimal('700.00'),
            created_by=user
        )
        print(f"   ✓ Created Production Order: {po.po_number}")
        
        # Check for GL entries
        after_count = JournalEntry.objects.filter(
            reference__startswith='MFG-'
        ).count()
        
        mfg_entry = JournalEntry.objects.filter(
            reference=f'MFG-{po.po_number}'
        ).first()
        
        if mfg_entry:
            print(f"   ✅ GL INTEGRATION WORKING")
            print(f"      Created Journal Entry: {mfg_entry.reference}")
            lines = mfg_entry.lines.all()
            for line in lines:
                print(f"      - {line.account.name}: DR=${line.debit} CR=${line.credit}")
        else:
            print(f"   ⚠️  Journal Entry NOT found")
            print(f"      Total MFG entries before: {before_count}")
            print(f"      Total MFG entries after: {after_count}")
            if after_count > before_count:
                print(f"      ✓ New entries created: {after_count - before_count}")
            else:
                print(f"      ❌ NO new GL entries created")
                
except Exception as e:
    print(f"   ❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

print()

# ============================================================================
# TEST 3: PROCUREMENT MODULE
# ============================================================================
print("3️⃣  TESTING PROCUREMENT MODULE")
print("-" * 80)

try:
    from accounting.models import Vendor
    
    before_count = LedgerEntry.objects.filter(
        reference_number__startswith='PO-'
    ).count()
    print(f"   Existing PO entries: {before_count}")
    
    # Check if vendor exists
    vendor = Vendor.objects.filter(entity=entity).first()
    if not vendor:
        print("   ⚠️  No vendor found - creating test vendor")
        vendor = Vendor.objects.create(
            entity=entity,
            name="Test Vendor",
            email="test@vendor.com",
            phone="9876543210"
        )
    
    # Create purchase order
    po = PurchaseOrder.objects.create(
        entity=entity,
        vendor=vendor,
        po_number=f"TEST-PO-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        total_amount=Decimal('5000.00'),
        subtotal=Decimal('4500.00'),
        tax_amount=Decimal('500.00'),
        status='RECEIVED',
        is_approved=True,
        approved_by=user,
        created_by=user
    )
    print(f"   ✓ Created Purchase Order: {po.po_number}")
    
    # Create goods receipt to trigger GL posting
    gr = GoodsReceipt.objects.create(
        entity=entity,
        purchase_order=po,
        receipt_number=f"TEST-GR-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        receipt_date=timezone.now().date(),
        status='RECEIVED',
        received_by=user
    )
    print(f"   ✓ Created Goods Receipt: {gr.receipt_number}")
    
    # Check for GL entries
    after_count = LedgerEntry.objects.filter(
        reference_number__startswith='PO-'
    ).count()
    
    po_entries = LedgerEntry.objects.filter(
        reference_number__contains=str(po.id)
    )
    
    gr_entries = LedgerEntry.objects.filter(
        reference_number__contains=str(gr.id)
    )
    
    if po_entries.exists() or gr_entries.exists():
        total_entries = po_entries.count() + gr_entries.count()
        print(f"   ✅ GL INTEGRATION WORKING")
        print(f"      Created {total_entries} ledger entries")
        for entry in list(po_entries) + list(gr_entries):
            print(f"      - {entry.entry_type}: {entry.account.name} = ${entry.amount}")
    else:
        print(f"   ⚠️  GL entries NOT found")
        print(f"      Total PO entries before: {before_count}")
        print(f"      Total PO entries after: {after_count}")
        if after_count > before_count:
            print(f"      ✓ New entries created: {after_count - before_count}")
        else:
            print(f"      ❌ NO new GL entries created")
            
except Exception as e:
    print(f"   ❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

print()

# ============================================================================
# TEST 4: EXPENSES MODULE
# ============================================================================
print("4️⃣  TESTING EXPENSES MODULE")
print("-" * 80)

try:
    before_count = LedgerEntry.objects.filter(
        reference_number__startswith='EXP-'
    ).count()
    print(f"   Existing EXP entries: {before_count}")
    
    # Check for expense category
    category = ExpenseCategory.objects.filter(entity=entity).first()
    if not category:
        print("   ⚠️  No expense category found - creating test category")
        
        # Find or create expense account
        expense_account = Account.objects.filter(
            entity=entity,
            account_type='EXPENSE'
        ).first()
        
        if not expense_account:
            print("   ❌ SKIPPED: No expense account found")
            category = None
        else:
            category = ExpenseCategory.objects.create(
                entity=entity,
                name="Test Travel Expense",
                code=f"TEST-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                expense_account=expense_account
            )
    
    # Check for employee
    employee = Employee.objects.filter(entity=entity, status='ACTIVE').first()
    if not employee:
        print("   ⚠️  No active employee found - cannot test")
        employee = None
    
    if category and employee:
        # Create expense report
        report = EmployeeExpenseReport.objects.create(
            entity=entity,
            employee=employee,
            report_number=f"TEST-EXP-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            period_start=timezone.now().date(),
            period_end=timezone.now().date(),
            status='APPROVED'
        )
        print(f"   ✓ Created Expense Report: {report.report_number}")
        
        # Create expense item
        expense = EmployeeExpense.objects.create(
            report=report,
            category=category,
            expense_date=timezone.now().date(),
            description="Test travel expense",
            amount=Decimal('150.00'),
            status='APPROVED'
        )
        print(f"   ✓ Created Expense Item: ${expense.amount}")
        
        # Post to GL
        result = expense.post_to_gl()
        print(f"   ✓ Called post_to_gl(): {result}")
        
        # Check for GL entries
        after_count = LedgerEntry.objects.filter(
            reference_number__startswith='EXP-'
        ).count()
        
        exp_entries = LedgerEntry.objects.filter(
            reference_number=f'EXP-{report.id}-{expense.id}'
        )
        
        if exp_entries.exists():
            print(f"   ✅ GL INTEGRATION WORKING")
            print(f"      Created {exp_entries.count()} ledger entries")
            for entry in exp_entries:
                print(f"      - {entry.entry_type}: {entry.account.name} = ${entry.amount}")
        else:
            print(f"   ⚠️  GL entries NOT found")
            print(f"      Total EXP entries before: {before_count}")
            print(f"      Total EXP entries after: {after_count}")
            if after_count > before_count:
                print(f"      ✓ New entries created: {after_count - before_count}")
            else:
                print(f"      ❌ NO new GL entries created")
    else:
        print(f"   ❌ SKIPPED: Missing category or employee")
        
except Exception as e:
    print(f"   ❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

print()

# ============================================================================
# TEST 5: HR MODULE
# ============================================================================
print("5️⃣  TESTING HR MODULE")
print("-" * 80)

try:
    before_count = LedgerEntry.objects.filter(
        reference_number__startswith='PAY-'
    ).count()
    print(f"   Existing PAY entries: {before_count}")
    
    # Check for employee and position
    employee = Employee.objects.filter(entity=entity, status='ACTIVE').first()
    if not employee:
        print("   ⚠️  No active employee - cannot test")
    else:
        position = employee.position
        if not position or not position.salary_expense_account:
            print("   ⚠️  Employee position missing or no salary expense account")
            print("   ❌ SKIPPED: Cannot test without salary account")
        else:
            # Create payroll
            payroll = Payroll.objects.create(
                entity=entity,
                payroll_number=f"TEST-PAY-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                period_start=timezone.now().date().replace(day=1),
                period_end=timezone.now().date(),
                status='APPROVED',
                approved_by=user,
                created_by=user
            )
            print(f"   ✓ Created Payroll: {payroll.payroll_number}")
            
            # Create payroll record
            record = PayrollRecord.objects.create(
                payroll=payroll,
                employee=employee,
                basic_salary=employee.salary or Decimal('5000.00'),
                total_gross=employee.salary or Decimal('5000.00'),
                total_deductions=Decimal('500.00'),
                total_net=Decimal('4500.00')
            )
            print(f"   ✓ Created Payroll Record for {employee.get_full_name()}")
            
            # Note: HR module requires manual GL posting via view
            # Check if payroll is marked as posted
            if payroll.is_posted:
                print(f"   ✓ Payroll is marked as posted to GL")
            else:
                print(f"   ⚠️  Payroll NOT posted to GL (requires manual posting via UI)")
            
            # Check for GL entries
            after_count = LedgerEntry.objects.filter(
                reference_number__startswith='PAY-'
            ).count()
            
            pay_entries = LedgerEntry.objects.filter(
                reference_number__contains=payroll.payroll_number
            )
            
            if pay_entries.exists():
                print(f"   ✅ GL INTEGRATION WORKING")
                print(f"      Created {pay_entries.count()} ledger entries")
                for entry in pay_entries:
                    print(f"      - {entry.entry_type}: {entry.account.name} = ${entry.amount}")
            else:
                print(f"   ℹ️  GL entries NOT found (HR requires manual posting)")
                print(f"      Total PAY entries in system: {after_count}")
                if after_count > 0:
                    print(f"      ✓ Other payroll entries exist in system")
                
except Exception as e:
    print(f"   ❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

print()

# ============================================================================
# TEST 6: MAINTENANCE MODULE
# ============================================================================
print("6️⃣  TESTING MAINTENANCE MODULE")
print("-" * 80)

try:
    before_count = LedgerEntry.objects.filter(
        reference_number__startswith='WO-'
    ).count()
    print(f"   Existing WO entries: {before_count}")
    
    # Check for maintenance asset
    asset = MaintenanceAsset.objects.filter(entity=entity).first()
    if not asset:
        print("   ⚠️  No maintenance asset found - creating test asset")
        asset = MaintenanceAsset.objects.create(
            entity=entity,
            asset_code=f"TEST-ASSET-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            asset_name="Test Equipment",
            asset_type="EQUIPMENT",
            location="Test Location",
            purchase_date=timezone.now().date(),
            acquisition_cost=Decimal('10000.00'),
            status='OPERATIONAL'
        )
    
    # Create work order
    wo = WorkOrder.objects.create(
        entity=entity,
        work_order_number=f"TEST-WO-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        asset=asset,
        work_order_type="CORRECTIVE",
        priority="MEDIUM",
        description="Test maintenance work",
        scheduled_date=timezone.now().date(),
        completion_date=timezone.now().date(),
        status="COMPLETED",
        assigned_to=user
    )
    print(f"   ✓ Created Work Order: {wo.work_order_number}")
    
    # Check for GL entries
    after_count = LedgerEntry.objects.filter(
        reference_number__startswith='WO-'
    ).count()
    
    wo_entries = LedgerEntry.objects.filter(
        reference_number__contains=str(wo.id)
    )
    
    if wo_entries.exists():
        print(f"   ✅ GL INTEGRATION WORKING")
        print(f"      Created {wo_entries.count()} ledger entries")
        for entry in wo_entries:
            print(f"      - {entry.entry_type}: {entry.account.name} = ${entry.amount}")
    else:
        print(f"   ❌ GL INTEGRATION NOT IMPLEMENTED")
        print(f"      Total WO entries before: {before_count}")
        print(f"      Total WO entries after: {after_count}")
        print(f"      📝 This confirms maintenance module needs GL integration")
        
except Exception as e:
    print(f"   ❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 80)
print("TEST COMPLETE")
print("=" * 80)
'''
        
        # Write test script to remote server
        print(f"\n📝 Uploading test script...")
        sftp = ssh.open_sftp()
        remote_script = '/tmp/test_module_gl_integration.py'
        with sftp.file(remote_script, 'w') as f:
            f.write(test_script)
        sftp.close()
        print(f"✅ Script uploaded to {remote_script}")
        
        # Execute test script
        print(f"\n🧪 Running integration tests...\n")
        print("=" * 80)
        
        # Use the virtual environment Python
        command = f'cd /var/www/tradifyerp && /var/www/tradifyerp/venv/bin/python {remote_script}'
        output, error = run_remote_command(ssh, command)
        
        print(output)
        
        if error and 'Traceback' in error:
            print("\n❌ ERRORS ENCOUNTERED:")
            print(error)
        
        print("=" * 80)
        
        # Cleanup
        print(f"\n🧹 Cleaning up...")
        run_remote_command(ssh, f'rm {remote_script}')
        print(f"✅ Test script removed")
        
        ssh.close()
        print(f"\n✅ Test completed successfully")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
