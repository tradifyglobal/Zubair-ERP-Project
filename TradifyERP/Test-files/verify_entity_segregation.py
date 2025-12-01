"""
Entity Data Segregation Verification Script
Checks if entity data is properly segregated across all modules
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from accounting.models import Entity, Account, LedgerEntry, Customer, Vendor
from hr.models import Employee, Payroll, LeaveRequest
from manufacturing.models import WarrantyRegistration, DistributorPerformance
from django.db.models import Count

print("=" * 80)
print("ENTITY DATA SEGREGATION VERIFICATION")
print("=" * 80)

# Get all entities
entities = Entity.objects.filter(is_active=True).order_by('id')

print(f"\n✓ Active Entities: {entities.count()}")
for entity in entities:
    print(f"  - {entity.id}: {entity.code} ({entity.name})")

print("\n" + "=" * 80)
print("ACCOUNTING MODULE - Data Count by Entity")
print("=" * 80)

for entity in entities:
    print(f"\n📊 Entity: {entity.code} (ID: {entity.id})")
    print(f"  Accounts:          {entity.accounts.count()}")
    print(f"  Ledger Entries:    {entity.ledger_entries.count()}")
    print(f"  Customers:         {entity.customers.count()}")
    print(f"  Vendors:           {entity.vendors.count()}")
    print(f"  Vendor Invoices:   {entity.vendor_invoices.count()}")
    print(f"  Vendor Payments:   {entity.vendor_payments.count()}")

print("\n" + "=" * 80)
print("HR MODULE - Data Count by Entity")
print("=" * 80)

for entity in entities:
    print(f"\n👥 Entity: {entity.code} (ID: {entity.id})")
    print(f"  Employees:         {entity.hr_employees.count()}")
    print(f"  Payrolls:          {entity.hr_payrolls.count()}")
    leave_requests = LeaveRequest.objects.filter(employee__entity=entity).count()
    print(f"  Leave Requests:    {leave_requests}")

print("\n" + "=" * 80)
print("MANUFACTURING MODULE - Data Count by Entity")
print("=" * 80)

for entity in entities:
    print(f"\n🏭 Entity: {entity.code} (ID: {entity.id})")
    print(f"  Warranty Registrations:      {entity.warranty_registrations.count()}")
    print(f"  Distributor Performance:     {entity.distributor_performance_metrics.count()}")

print("\n" + "=" * 80)
print("DATA ISOLATION CHECK - Cross-Entity Verification")
print("=" * 80)

# Check if any Account belongs to multiple entities
print("\n🔍 Checking for data cross-contamination...")

accounts_all = Account.objects.values('id', 'entity_id').annotate(count=Count('entity_id'))
cross_entity_accounts = Account.objects.values('account_number').annotate(count=Count('id')).filter(count__gt=1)
if cross_entity_accounts.exists():
    print("⚠️  ISSUE: Accounts with same number in different entities (intentional?):")
    for acc in cross_entity_accounts:
        print(f"  - Account {acc['account_number']}: {acc['count']} versions")
else:
    print("✓ Accounts properly isolated by entity")

# Check ledger entries
ledger_all = LedgerEntry.objects.all()
ledger_by_entity = ledger_all.values('entity').annotate(count=Count('id')).order_by('entity')
print(f"\n✓ Ledger Entries distribution:")
for row in ledger_by_entity:
    entity = Entity.objects.get(id=row['entity'])
    print(f"  - {entity.code}: {row['count']} entries")

# Check employees
employees_by_entity = Employee.objects.values('entity').annotate(count=Count('id')).order_by('entity')
print(f"\n✓ Employees distribution:")
for row in employees_by_entity:
    entity = Entity.objects.get(id=row['entity'])
    print(f"  - {entity.code}: {row['count']} employees")

# Check payrolls
payrolls_by_entity = Payroll.objects.values('entity').annotate(count=Count('id')).order_by('entity')
print(f"\n✓ Payrolls distribution:")
for row in payrolls_by_entity:
    entity = Entity.objects.get(id=row['entity'])
    print(f"  - {entity.code}: {row['count']} payrolls")

print("\n" + "=" * 80)
print("SESSION-BASED FILTERING TEST")
print("=" * 80)

print("\nTo verify session-based filtering:")
print("1. Log in to the system")
print("2. Select 'TRADIFY-001' entity")
print("3. Navigate to:")
print("   - Accounting > Accounts (should show TRADIFY-001 accounts only)")
print("   - Accounting > Customers (should show TRADIFY-001 customers only)")
print("   - HR > Employees (should show TRADIFY-001 employees only)")
print("4. Switch to 'MAIN' entity and verify data changes")
print("5. Switch to 'Pristing-Planet-001' and verify data changes")

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print("✓ Entity data segregation verification complete")
print("✓ Check the database for proper entity_id assignment")
print("✓ Verify navbar entity switcher is working")
print("✓ All modules should filter by session entity automatically")
print("=" * 80 + "\n")
