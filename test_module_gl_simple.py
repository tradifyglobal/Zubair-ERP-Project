"""
Test Module → Accounting Integration (via Django shell)
Creates test transactions and verifies GL posting
"""

import paramiko
import sys
from datetime import datetime

def run_remote_command(ssh, command, timeout=60):
    """Execute command on remote server and return output"""
    stdin, stdout, stderr = ssh.exec_command(command, timeout=timeout)
    output = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')
    return output, error

def main():
    # Server credentials
    host = '192.168.2.69'
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
        print(f"✅ Connected successfully\n")
        
        # Create comprehensive test commands using manage.py shell_plus or shell
        tests = [
            ("Sales Module", """
from sales.models import Invoice, Customer
from accounting.models import LedgerEntry, Account, Entity
from django.contrib.auth.models import User
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta

entity = Entity.objects.first()
user = User.objects.first()
print(f"Using Entity: {entity.name}")

# Count before
before = LedgerEntry.objects.filter(reference_number__startswith='INV-').count()
print(f"Existing INV entries: {before}")

# Get or create customer
customer, _ = Customer.objects.get_or_create(
    entity=entity, email='test@customer.com',
    defaults={'name': 'Test Customer', 'phone': '1234567890'}
)

# Check GL accounts
ar_account = Account.objects.filter(entity=entity, account_type='ASSET', name__icontains='receivable').first()
revenue_account = Account.objects.filter(entity=entity, account_type='INCOME', name__icontains='sales').first()

if ar_account and revenue_account:
    # Create invoice
    invoice = Invoice.objects.create(
        entity=entity, customer=customer,
        invoice_number=f'TEST-INV-{timezone.now().strftime("%Y%m%d%H%M%S")}',
        invoice_date=timezone.now().date(),
        due_date=timezone.now().date() + timedelta(days=30),
        subtotal=Decimal('1000.00'), tax_amount=Decimal('100.00'),
        total_amount=Decimal('1100.00'), status='ISSUED', issued_by=user
    )
    print(f"Created Invoice: {invoice.invoice_number}")
    
    # Check GL entries
    entries = LedgerEntry.objects.filter(reference_number__contains=str(invoice.id))
    after = LedgerEntry.objects.filter(reference_number__startswith='INV-').count()
    
    if entries.exists():
        print(f"✅ GL WORKING: {entries.count()} entries")
        for e in entries: print(f"  {e.entry_type}: {e.account.name} = ${e.amount}")
    else:
        print(f"⚠️ No specific entries found. Total before: {before}, after: {after}")
else:
    print("❌ Missing GL accounts")
"""),

            ("Manufacturing Module", """
from manufacturing.models import ProductionOrder, Product
from accounting.models import JournalEntry, Account, Entity
from django.contrib.auth.models import User
from decimal import Decimal
from django.utils import timezone

entity = Entity.objects.first()
user = User.objects.first()

# Count before
before = JournalEntry.objects.filter(reference__startswith='MFG-').count()
print(f"Existing MFG entries: {before}")

# Get or create product
inv_account = Account.objects.filter(entity=entity, account_type='ASSET').first()
if inv_account:
    product, _ = Product.objects.get_or_create(
        entity=entity, product_code=f'TEST-PROD-{timezone.now().strftime("%Y%m%d%H%M%S")}',
        defaults={'name': 'Test Product', 'unit_of_measure': 'PCS', 'inventory_account': inv_account}
    )
    
    # Create production order
    po = ProductionOrder.objects.create(
        entity=entity, po_number=f'TEST-MFG-{timezone.now().strftime("%Y%m%d%H%M%S")}',
        product=product, quantity_planned=Decimal('10'), quantity_completed=Decimal('10'),
        status='COMPLETE', start_date=timezone.now().date(), due_date=timezone.now().date(),
        actual_material_cost=Decimal('500'), actual_labor_cost=Decimal('200'),
        total_actual_cost=Decimal('700'), created_by=user
    )
    print(f"Created PO: {po.po_number}")
    
    # Check GL
    entry = JournalEntry.objects.filter(reference=f'MFG-{po.po_number}').first()
    after = JournalEntry.objects.filter(reference__startswith='MFG-').count()
    
    if entry:
        print(f"✅ GL WORKING: {entry.reference}")
        for line in entry.lines.all(): print(f"  {line.account.name}: DR=${line.debit} CR=${line.credit}")
    else:
        print(f"⚠️ No entry found. Total before: {before}, after: {after}")
else:
    print("❌ No inventory account")
"""),

            ("Procurement Module", """
from procurement.models import PurchaseOrder, GoodsReceipt
from accounting.models import LedgerEntry, Vendor, Entity
from django.contrib.auth.models import User
from decimal import Decimal
from django.utils import timezone

entity = Entity.objects.first()
user = User.objects.first()

before = LedgerEntry.objects.filter(reference_number__startswith='PO-').count()
print(f"Existing PO entries: {before}")

vendor, _ = Vendor.objects.get_or_create(
    entity=entity, email='test@vendor.com',
    defaults={'name': 'Test Vendor', 'phone': '9876543210'}
)

po = PurchaseOrder.objects.create(
    entity=entity, vendor=vendor,
    po_number=f'TEST-PO-{timezone.now().strftime("%Y%m%d%H%M%S")}',
    total_amount=Decimal('5000'), subtotal=Decimal('4500'),
    tax_amount=Decimal('500'), status='RECEIVED',
    is_approved=True, approved_by=user, created_by=user
)
print(f"Created PO: {po.po_number}")

gr = GoodsReceipt.objects.create(
    entity=entity, purchase_order=po,
    receipt_number=f'TEST-GR-{timezone.now().strftime("%Y%m%d%H%M%S")}',
    receipt_date=timezone.now().date(), status='RECEIVED', received_by=user
)
print(f"Created GR: {gr.receipt_number}")

entries = LedgerEntry.objects.filter(reference_number__contains=str(po.id))
gr_entries = LedgerEntry.objects.filter(reference_number__contains=str(gr.id))
after = LedgerEntry.objects.filter(reference_number__startswith='PO-').count()

if entries.exists() or gr_entries.exists():
    total = entries.count() + gr_entries.count()
    print(f"✅ GL WORKING: {total} entries")
    for e in list(entries) + list(gr_entries): print(f"  {e.entry_type}: {e.account.name} = ${e.amount}")
else:
    print(f"⚠️ No entries. Before: {before}, after: {after}")
"""),

            ("Expenses Module", """
from expenses.models import EmployeeExpense, EmployeeExpenseReport, ExpenseCategory
from hr.models import Employee
from accounting.models import LedgerEntry, Account, Entity
from decimal import Decimal
from django.utils import timezone

entity = Entity.objects.first()

before = LedgerEntry.objects.filter(reference_number__startswith='EXP-').count()
print(f"Existing EXP entries: {before}")

expense_account = Account.objects.filter(entity=entity, account_type='EXPENSE').first()
employee = Employee.objects.filter(entity=entity, status='ACTIVE').first()

if expense_account and employee:
    category, _ = ExpenseCategory.objects.get_or_create(
        entity=entity, code=f'TEST-{timezone.now().strftime("%Y%m%d%H%M%S")}',
        defaults={'name': 'Test Travel', 'expense_account': expense_account}
    )
    
    report = EmployeeExpenseReport.objects.create(
        entity=entity, employee=employee,
        report_number=f'TEST-EXP-{timezone.now().strftime("%Y%m%d%H%M%S")}',
        period_start=timezone.now().date(), period_end=timezone.now().date(),
        status='APPROVED'
    )
    print(f"Created Report: {report.report_number}")
    
    expense = EmployeeExpense.objects.create(
        report=report, category=category, expense_date=timezone.now().date(),
        description='Test expense', amount=Decimal('150'), status='APPROVED'
    )
    result = expense.post_to_gl()
    print(f"Posted to GL: {result}")
    
    entries = LedgerEntry.objects.filter(reference_number=f'EXP-{report.id}-{expense.id}')
    after = LedgerEntry.objects.filter(reference_number__startswith='EXP-').count()
    
    if entries.exists():
        print(f"✅ GL WORKING: {entries.count()} entries")
        for e in entries: print(f"  {e.entry_type}: {e.account.name} = ${e.amount}")
    else:
        print(f"⚠️ No entries. Before: {before}, after: {after}")
else:
    print("❌ Missing account or employee")
"""),

            ("HR Module", """
from hr.models import Payroll, PayrollRecord, Employee
from accounting.models import LedgerEntry, Entity
from django.contrib.auth.models import User
from decimal import Decimal
from django.utils import timezone

entity = Entity.objects.first()
user = User.objects.first()

before = LedgerEntry.objects.filter(reference_number__startswith='PAY-').count()
print(f"Existing PAY entries: {before}")

employee = Employee.objects.filter(entity=entity, status='ACTIVE').first()

if employee and employee.position and employee.position.salary_expense_account:
    payroll = Payroll.objects.create(
        entity=entity, payroll_number=f'TEST-PAY-{timezone.now().strftime("%Y%m%d%H%M%S")}',
        period_start=timezone.now().date().replace(day=1),
        period_end=timezone.now().date(),
        status='APPROVED', approved_by=user, created_by=user
    )
    print(f"Created Payroll: {payroll.payroll_number}")
    
    record = PayrollRecord.objects.create(
        payroll=payroll, employee=employee,
        basic_salary=employee.salary or Decimal('5000'),
        total_gross=employee.salary or Decimal('5000'),
        total_deductions=Decimal('500'), total_net=Decimal('4500')
    )
    print(f"Created Record for {employee.get_full_name()}")
    
    entries = LedgerEntry.objects.filter(reference_number__contains=payroll.payroll_number)
    after = LedgerEntry.objects.filter(reference_number__startswith='PAY-').count()
    
    if entries.exists():
        print(f"✅ GL WORKING: {entries.count()} entries")
        for e in entries: print(f"  {e.entry_type}: {e.account.name} = ${e.amount}")
    else:
        print(f"ℹ️ HR requires manual posting. Total PAY entries: {after}")
        print(f"  (Payroll created but not posted - needs UI action)")
else:
    print("❌ No employee with salary account")
"""),

            ("Maintenance Module", """
from maintenance.models import WorkOrder, MaintenanceAsset
from accounting.models import LedgerEntry, Entity
from django.contrib.auth.models import User
from decimal import Decimal
from django.utils import timezone

entity = Entity.objects.first()
user = User.objects.first()

before = LedgerEntry.objects.filter(reference_number__startswith='WO-').count()
print(f"Existing WO entries: {before}")

asset, _ = MaintenanceAsset.objects.get_or_create(
    entity=entity, asset_code=f'TEST-ASSET-{timezone.now().strftime("%Y%m%d%H%M%S")}',
    defaults={'asset_name': 'Test Equipment', 'asset_type': 'EQUIPMENT',
              'location': 'Test', 'purchase_date': timezone.now().date(),
              'acquisition_cost': Decimal('10000'), 'status': 'OPERATIONAL'}
)

wo = WorkOrder.objects.create(
    entity=entity, work_order_number=f'TEST-WO-{timezone.now().strftime("%Y%m%d%H%M%S")}',
    asset=asset, work_order_type='CORRECTIVE', priority='MEDIUM',
    description='Test work', scheduled_date=timezone.now().date(),
    completion_date=timezone.now().date(), status='COMPLETED', assigned_to=user
)
print(f"Created WO: {wo.work_order_number}")

entries = LedgerEntry.objects.filter(reference_number__contains=str(wo.id))
after = LedgerEntry.objects.filter(reference_number__startswith='WO-').count()

if entries.exists():
    print(f"✅ GL WORKING: {entries.count()} entries")
    for e in entries: print(f"  {e.entry_type}: {e.account.name} = ${e.amount}")
else:
    print(f"❌ GL NOT IMPLEMENTED")
    print(f"  Total before: {before}, after: {after}")
    print(f"  Maintenance module needs GL integration")
"""),
        ]
        
        # Run each test
        for i, (module_name, test_code) in enumerate(tests, 1):
            print(f"\n{'='*80}")
            print(f"{i}️⃣  TESTING {module_name.upper()}")
            print(f"{'='*80}\n")
            
            # Create shell command
            shell_cmd = f"cd /var/www/tradifyerp && /var/www/tradifyerp/venv/bin/python manage.py shell -c \"{test_code.replace('\\n', ' ').replace('\"', '\\\"')}\""
            
            # Execute
            output, error = run_remote_command(ssh, shell_cmd, timeout=90)
            
            if output:
                print(output)
            if error and ('Error' in error or 'Traceback' in error):
                print(f"⚠️ Errors:\n{error}")
        
        print(f"\n{'='*80}")
        print(f"TEST SUMMARY")
        print(f"{'='*80}\n")
        
        # Get summary stats
        summary_cmd = f"""cd /var/www/tradifyerp && /var/www/tradifyerp/venv/bin/python manage.py shell -c "
from accounting.models import LedgerEntry
from accounting.models import JournalEntry

inv_count = LedgerEntry.objects.filter(reference_number__startswith='INV-').count()
mfg_count = JournalEntry.objects.filter(reference__startswith='MFG-').count()
po_count = LedgerEntry.objects.filter(reference_number__startswith='PO-').count()
exp_count = LedgerEntry.objects.filter(reference_number__startswith='EXP-').count()
pay_count = LedgerEntry.objects.filter(reference_number__startswith='PAY-').count()
wo_count = LedgerEntry.objects.filter(reference_number__startswith='WO-').count()

print(f'Sales (INV-): {inv_count} entries')
print(f'Manufacturing (MFG-): {mfg_count} entries')
print(f'Procurement (PO-/GR-): {po_count} entries')
print(f'Expenses (EXP-): {exp_count} entries')
print(f'HR/Payroll (PAY-): {pay_count} entries')
print(f'Maintenance (WO-): {wo_count} entries')
"
"""
        output, error = run_remote_command(ssh, summary_cmd, timeout=30)
        print(output)
        
        ssh.close()
        print(f"\n✅ Test completed successfully")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
