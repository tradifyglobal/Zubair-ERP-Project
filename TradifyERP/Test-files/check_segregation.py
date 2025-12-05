#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from accounting.models import Entity, Account, LedgerEntry, Customer, Vendor
from hr.models import Employee, Payroll, PayrollRecord
from manufacturing.models import WarrantyRegistration, DistributorPerformance
from django.db.models import Count

print("\n" + "="*80)
print("DATA SEGREGATION CHECK - BY ENTITY")
print("="*80)

# Get all entities
entities = Entity.objects.all()

for entity in entities:
    print(f"\n{'='*80}")
    print(f"ENTITY: {entity.code} ({entity.name}) - ID: {entity.id}")
    print(f"{'='*80}")
    
    # Accounting Module
    print(f"\n📊 ACCOUNTING MODULE:")
    print(f"  • Accounts:        {entity.accounts.count()}")
    print(f"  • Customers:       {entity.customers.count()}")
    print(f"  • Vendors:         {entity.vendors.count()}")
    print(f"  • Ledger Entries:  {entity.ledger_entries.count()}")
    
    # Show sample accounts
    if entity.accounts.exists():
        print(f"    Sample accounts:")
        for acc in entity.accounts.all()[:3]:
            print(f"      - {acc.account_number}: {acc.name} ({acc.account_type})")
    
    # HR Module
    print(f"\n👥 HR MODULE:")
    employees = Employee.objects.filter(entity=entity)
    payrolls = Payroll.objects.filter(entity=entity)
    print(f"  • Employees:       {employees.count()}")
    print(f"  • Payrolls:        {payrolls.count()}")
    
    # Show sample employees
    if employees.exists():
        print(f"    Sample employees:")
        for emp in employees.all()[:3]:
            print(f"      - {emp.employee_id}: {emp.first_name} {emp.last_name} ({emp.status})")
    
    # Manufacturing Module
    print(f"\n🏭 MANUFACTURING MODULE:")
    warranties = WarrantyRegistration.objects.filter(entity=entity)
    distributors = DistributorPerformance.objects.filter(entity=entity)
    print(f"  • Warranty Registrations: {warranties.count()}")
    print(f"  • Distributor Performance: {distributors.count()}")
    
    # Show sample warranties
    if warranties.exists():
        print(f"    Sample warranties:")
        for w in warranties.all()[:3]:
            print(f"      - {w.warranty_number}: {w.product_code}")
    
    # Show sample distributor performance
    if distributors.exists():
        print(f"    Sample distributor performance:")
        for d in distributors.all()[:3]:
            print(f"      - {d.distributor.distributor_name} ({d.performance_month}/{d.performance_year})")

print(f"\n{'='*80}")
print("DATA SEGREGATION SUMMARY")
print(f"{'='*80}")

total_accounts = Account.objects.count()
total_customers = Customer.objects.count()
total_vendors = Vendor.objects.count()
total_ledger = LedgerEntry.objects.count()
total_employees = Employee.objects.count()
total_payrolls = Payroll.objects.count()
total_warranties = WarrantyRegistration.objects.count()
total_distributors = DistributorPerformance.objects.count()

print(f"\nGLOBAL TOTALS (All Entities Combined):")
print(f"  Accounting: {total_accounts} accounts, {total_customers} customers, {total_vendors} vendors, {total_ledger} ledger entries")
print(f"  HR:         {total_employees} employees, {total_payrolls} payrolls")
print(f"  Manufacturing: {total_warranties} warranties, {total_distributors} distributor records")

print(f"\n✓ Checking for orphaned records (records with null entity)...")

# Check for orphaned records
orphaned_accounts = Account.objects.filter(entity__isnull=True).count()
orphaned_customers = Customer.objects.filter(entity__isnull=True).count()
orphaned_vendors = Vendor.objects.filter(entity__isnull=True).count()
orphaned_employees = Employee.objects.filter(entity__isnull=True).count()
orphaned_payrolls = Payroll.objects.filter(entity__isnull=True).count()
orphaned_warranties = WarrantyRegistration.objects.filter(entity__isnull=True).count()
orphaned_distributors = DistributorPerformance.objects.filter(entity__isnull=True).count()

if any([orphaned_accounts, orphaned_customers, orphaned_vendors, orphaned_employees, 
        orphaned_payrolls, orphaned_warranties, orphaned_distributors]):
    print(f"\n⚠️  WARNING - ORPHANED RECORDS FOUND:")
    if orphaned_accounts: print(f"  ❌ {orphaned_accounts} Accounts with no entity")
    if orphaned_customers: print(f"  ❌ {orphaned_customers} Customers with no entity")
    if orphaned_vendors: print(f"  ❌ {orphaned_vendors} Vendors with no entity")
    if orphaned_employees: print(f"  ❌ {orphaned_employees} Employees with no entity")
    if orphaned_payrolls: print(f"  ❌ {orphaned_payrolls} Payrolls with no entity")
    if orphaned_warranties: print(f"  ❌ {orphaned_warranties} Warranties with no entity")
    if orphaned_distributors: print(f"  ❌ {orphaned_distributors} Distributor records with no entity")
else:
    print(f"  ✅ No orphaned records found - All data properly assigned to entities")

print(f"\n{'='*80}\n")
