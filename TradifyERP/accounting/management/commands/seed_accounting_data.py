"""
Management command to seed accounting data for testing.
Creates a sample entity, chart of accounts, and initial journal entries.

Usage: python manage.py seed_accounting_data
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from accounting.models import Entity, Currency, Account, LedgerEntry, Customer, Vendor, AuditLog


class Command(BaseCommand):
    help = 'Seeds the accounting database with sample data'

    def handle(self, *args, **options):
        self.stdout.write("Starting accounting data seed...")

        # Create Currency (USD)
        usd, created = Currency.objects.get_or_create(
            code='USD',
            defaults={
                'name': 'US Dollar',
                'symbol': '$',
                'is_active': True,
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('✓ Created Currency: USD'))
        else:
            self.stdout.write('USD Currency already exists')

        # Create Entity (Company)
        entity, created = Entity.objects.get_or_create(
            code='TRADIFY-001',
            defaults={
                'name': 'Tradify ERP Corporation',
                'description': 'Main company for Tradify ERP',
                'is_active': True,
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('✓ Created Entity: TRADIFY-001'))
        else:
            self.stdout.write('Entity TRADIFY-001 already exists')

        # Create Chart of Accounts
        accounts_data = [
            # Assets
            ('1010', 'Cash', 'ASSET', 'Bank and cash on hand'),
            ('1020', 'Accounts Receivable', 'ASSET', 'Money owed by customers'),
            ('1030', 'Inventory', 'ASSET', 'Goods held for sale'),
            ('1040', 'Prepaid Expenses', 'ASSET', 'Payments made in advance'),
            ('1500', 'Equipment', 'ASSET', 'Machinery and equipment'),
            ('1510', 'Accumulated Depreciation', 'ASSET', 'Depreciation on equipment'),

            # Liabilities
            ('2010', 'Accounts Payable', 'LIABILITY', 'Money owed to suppliers'),
            ('2020', 'Short-term Debt', 'LIABILITY', 'Loans due within one year'),
            ('2030', 'Accrued Expenses', 'LIABILITY', 'Expenses incurred but not paid'),
            ('2500', 'Long-term Debt', 'LIABILITY', 'Loans due after one year'),

            # Equity
            ('3010', 'Common Stock', 'EQUITY', 'Shareholder capital'),
            ('3020', 'Retained Earnings', 'EQUITY', 'Cumulative profits'),
            ('3030', 'Dividends', 'EQUITY', 'Distributions to shareholders'),

            # Income/Revenue
            ('4010', 'Sales Revenue', 'INCOME', 'Revenue from product sales'),
            ('4020', 'Service Revenue', 'INCOME', 'Revenue from services'),
            ('4030', 'Interest Income', 'INCOME', 'Interest earned'),

            # Expenses
            ('5010', 'Cost of Goods Sold', 'EXPENSE', 'Direct cost of inventory'),
            ('5020', 'Salaries & Wages', 'EXPENSE', 'Employee compensation'),
            ('5030', 'Rent Expense', 'EXPENSE', 'Office rent'),
            ('5040', 'Utilities Expense', 'EXPENSE', 'Electricity, water, etc.'),
            ('5050', 'Supplies Expense', 'EXPENSE', 'Office supplies'),
            ('5060', 'Depreciation Expense', 'EXPENSE', 'Equipment depreciation'),
            ('5070', 'Insurance Expense', 'EXPENSE', 'Business insurance'),
            ('5080', 'Office Equipment Rental', 'EXPENSE', 'Equipment rental costs'),
            ('5090', 'Professional Fees', 'EXPENSE', 'Accounting, legal fees'),
            ('5100', 'Marketing Expense', 'EXPENSE', 'Advertising and promotion'),
        ]

        created_accounts = []
        for code, name, account_type, description in accounts_data:
            account, created = Account.objects.get_or_create(
                entity=entity,
                account_number=code,
                defaults={
                    'name': name,
                    'account_type': account_type,
                    'description': description,
                    'is_active': True,
                    'currency': usd,
                }
            )
            if created:
                created_accounts.append(account)

        self.stdout.write(self.style.SUCCESS(f'✓ Created {len(created_accounts)} Chart of Accounts'))

        # Create Sample Customers
        customers_data = [
            ('CUST-001', 'Acme Corporation', 'contact@acme.com', '+1-555-0101'),
            ('CUST-002', 'TechStart Inc', 'sales@techstart.com', '+1-555-0102'),
            ('CUST-003', 'Global Solutions Ltd', 'info@globalsolutions.com', '+1-555-0103'),
        ]

        created_customers = []
        for code, name, email, phone in customers_data:
            customer, created = Customer.objects.get_or_create(
                entity=entity,
                customer_code=code,
                defaults={
                    'name': name,
                    'email': email,
                    'phone': phone,
                    'currency': usd,
                    'is_active': True,
                }
            )
            if created:
                created_customers.append(customer)

        self.stdout.write(self.style.SUCCESS(f'✓ Created {len(created_customers)} Sample Customers'))

        # Create Sample Vendors
        vendors_data = [
            ('VEND-001', 'Office Supply Co', 'orders@officesupply.com', '+1-555-0201'),
            ('VEND-002', 'Tech Equipment Supplier', 'sales@techequip.com', '+1-555-0202'),
            ('VEND-003', 'Utility Services Inc', 'billing@utilityservices.com', '+1-555-0203'),
        ]

        created_vendors = []
        for code, name, email, phone in vendors_data:
            vendor, created = Vendor.objects.get_or_create(
                entity=entity,
                vendor_code=code,
                defaults={
                    'name': name,
                    'email': email,
                    'phone': phone,
                    'currency': usd,
                    'is_active': True,
                }
            )
            if created:
                created_vendors.append(vendor)

        self.stdout.write(self.style.SUCCESS(f'✓ Created {len(created_vendors)} Sample Vendors'))

        # Create Sample Ledger Entries (Double-Entry Bookkeeping)
        base_date = timezone.now().date() - timedelta(days=30)
        entries_created = 0

        # Transaction 1: Initial Investment (Debit Cash / Credit Common Stock)
        if not LedgerEntry.objects.filter(
            entity=entity,
            description__contains='Initial investment'
        ).exists():
            cash_account = Account.objects.get(entity=entity, account_number='1010')
            stock_account = Account.objects.get(entity=entity, account_number='3010')

            LedgerEntry.objects.create(
                entity=entity,
                account=cash_account,
                entry_type='DEBIT',
                amount=Decimal('100000.00'),
                entry_date=base_date,
                description='Initial investment',
                is_posted=True,
            )
            LedgerEntry.objects.create(
                entity=entity,
                account=stock_account,
                entry_type='CREDIT',
                amount=Decimal('100000.00'),
                entry_date=base_date,
                description='Initial investment',
                is_posted=True,
            )
            entries_created += 2

        # Transaction 2: Purchase Equipment (Debit Equipment / Credit Cash)
        if not LedgerEntry.objects.filter(
            entity=entity,
            description__contains='Purchase equipment'
        ).exists():
            equipment_account = Account.objects.get(entity=entity, account_number='1500')
            cash_account = Account.objects.get(entity=entity, account_number='1010')

            LedgerEntry.objects.create(
                entity=entity,
                account=equipment_account,
                entry_type='DEBIT',
                amount=Decimal('25000.00'),
                entry_date=base_date + timedelta(days=1),
                description='Purchase equipment',
                is_posted=True,
            )
            LedgerEntry.objects.create(
                entity=entity,
                account=cash_account,
                entry_type='CREDIT',
                amount=Decimal('25000.00'),
                entry_date=base_date + timedelta(days=1),
                description='Purchase equipment',
                is_posted=True,
            )
            entries_created += 2

        # Transaction 3: Sales Revenue (Debit Cash / Credit Sales Revenue)
        if not LedgerEntry.objects.filter(
            entity=entity,
            description__contains='Sales revenue'
        ).exists():
            cash_account = Account.objects.get(entity=entity, account_number='1010')
            sales_account = Account.objects.get(entity=entity, account_number='4010')

            LedgerEntry.objects.create(
                entity=entity,
                account=cash_account,
                entry_type='DEBIT',
                amount=Decimal('15000.00'),
                entry_date=base_date + timedelta(days=5),
                description='Sales revenue',
                is_posted=True,
            )
            LedgerEntry.objects.create(
                entity=entity,
                account=sales_account,
                entry_type='CREDIT',
                amount=Decimal('15000.00'),
                entry_date=base_date + timedelta(days=5),
                description='Sales revenue',
                is_posted=True,
            )
            entries_created += 2

        # Transaction 4: Paid Salaries (Debit Salaries Expense / Credit Cash)
        if not LedgerEntry.objects.filter(
            entity=entity,
            description__contains='Paid salaries'
        ).exists():
            salaries_account = Account.objects.get(entity=entity, account_number='5020')
            cash_account = Account.objects.get(entity=entity, account_number='1010')

            LedgerEntry.objects.create(
                entity=entity,
                account=salaries_account,
                entry_type='DEBIT',
                amount=Decimal('8000.00'),
                entry_date=base_date + timedelta(days=10),
                description='Paid salaries',
                is_posted=True,
            )
            LedgerEntry.objects.create(
                entity=entity,
                account=cash_account,
                entry_type='CREDIT',
                amount=Decimal('8000.00'),
                entry_date=base_date + timedelta(days=10),
                description='Paid salaries',
                is_posted=True,
            )
            entries_created += 2

        # Transaction 5: Paid Rent (Debit Rent Expense / Credit Cash)
        if not LedgerEntry.objects.filter(
            entity=entity,
            description__contains='Paid rent'
        ).exists():
            rent_account = Account.objects.get(entity=entity, account_number='5030')
            cash_account = Account.objects.get(entity=entity, account_number='1010')

            LedgerEntry.objects.create(
                entity=entity,
                account=rent_account,
                entry_type='DEBIT',
                amount=Decimal('5000.00'),
                entry_date=base_date + timedelta(days=15),
                description='Paid rent',
                is_posted=True,
            )
            LedgerEntry.objects.create(
                entity=entity,
                account=cash_account,
                entry_type='CREDIT',
                amount=Decimal('5000.00'),
                entry_date=base_date + timedelta(days=15),
                description='Paid rent',
                is_posted=True,
            )
            entries_created += 2

        # Transaction 6: More Sales (Debit Cash / Credit Sales Revenue)
        if not LedgerEntry.objects.filter(
            entity=entity,
            description__contains='Additional sales'
        ).exists():
            cash_account = Account.objects.get(entity=entity, account_number='1010')
            sales_account = Account.objects.get(entity=entity, account_number='4010')

            LedgerEntry.objects.create(
                entity=entity,
                account=cash_account,
                entry_type='DEBIT',
                amount=Decimal('22000.00'),
                entry_date=base_date + timedelta(days=20),
                description='Additional sales',
                is_posted=True,
            )
            LedgerEntry.objects.create(
                entity=entity,
                account=sales_account,
                entry_type='CREDIT',
                amount=Decimal('22000.00'),
                entry_date=base_date + timedelta(days=20),
                description='Additional sales',
                is_posted=True,
            )
            entries_created += 2

        # Transaction 7: Utilities (Debit Utilities Expense / Credit Cash)
        if not LedgerEntry.objects.filter(
            entity=entity,
            description__contains='Utilities payment'
        ).exists():
            utilities_account = Account.objects.get(entity=entity, account_number='5040')
            cash_account = Account.objects.get(entity=entity, account_number='1010')

            LedgerEntry.objects.create(
                entity=entity,
                account=utilities_account,
                entry_type='DEBIT',
                amount=Decimal('1200.00'),
                entry_date=base_date + timedelta(days=25),
                description='Utilities payment',
                is_posted=True,
            )
            LedgerEntry.objects.create(
                entity=entity,
                account=cash_account,
                entry_type='CREDIT',
                amount=Decimal('1200.00'),
                entry_date=base_date + timedelta(days=25),
                description='Utilities payment',
                is_posted=True,
            )
            entries_created += 2

        if entries_created > 0:
            self.stdout.write(self.style.SUCCESS(f'✓ Created {entries_created} Sample Ledger Entries'))
        else:
            self.stdout.write('Sample ledger entries already exist')

        self.stdout.write(self.style.SUCCESS('\n✅ Accounting data seed completed successfully!'))
        self.stdout.write(f'\nSummary:')
        self.stdout.write(f'  - Entity: {entity.name} ({entity.code})')
        self.stdout.write(f'  - Chart of Accounts: {Account.objects.filter(entity=entity).count()} accounts')
        self.stdout.write(f'  - Customers: {Customer.objects.filter(entity=entity).count()}')
        self.stdout.write(f'  - Vendors: {Vendor.objects.filter(entity=entity).count()}')
        self.stdout.write(f'  - Ledger Entries: {LedgerEntry.objects.filter(entity=entity).count()}')
