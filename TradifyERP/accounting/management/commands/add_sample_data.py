from django.core.management.base import BaseCommand
from accounting.models import Entity, Account, Customer, Vendor, LedgerEntry
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal


class Command(BaseCommand):
    help = 'Add sample data for dashboard charts'

    def handle(self, *args, **options):
        # Get or create entity
        entity, created = Entity.objects.get_or_create(
            code='DEFAULT',
            defaults={
                'name': 'Default Entity',
                'is_active': True
            }
        )
        
        # Create sample accounts
        account_types = {
            'ASSET': ['Cash', 'Accounts Receivable', 'Equipment'],
            'LIABILITY': ['Accounts Payable', 'Notes Payable'],
            'EQUITY': ['Common Stock', 'Retained Earnings'],
        }
        
        for acc_type, names in account_types.items():
            for i, name in enumerate(names):
                Account.objects.get_or_create(
                    entity=entity,
                    code=f"{acc_type[:3]}-{i+1:03d}",
                    defaults={
                        'name': name,
                        'account_type': acc_type,
                        'currency': 'USD'
                    }
                )
        
        # Create sample customers
        for i in range(5):
            Customer.objects.get_or_create(
                entity=entity,
                customer_code=f'CUST-{i+1:03d}',
                defaults={
                    'name': f'Customer {i+1}',
                    'email': f'customer{i+1}@example.com',
                    'currency': 'USD'
                }
            )
        
        # Create sample vendors
        for i in range(5):
            Vendor.objects.get_or_create(
                entity=entity,
                vendor_code=f'VEND-{i+1:03d}',
                defaults={
                    'name': f'Vendor {i+1}',
                    'email': f'vendor{i+1}@example.com',
                    'currency': 'USD'
                }
            )
        
        # Create sample ledger entries for last 6 months
        cash_account = Account.objects.filter(entity=entity, code__startswith='ASS').first()
        if cash_account:
            end_date = timezone.now().date()
            for i in range(180, 0, -30):
                entry_date = end_date - timedelta(days=i)
                
                # Add debit entries
                LedgerEntry.objects.get_or_create(
                    entity=entity,
                    account=cash_account,
                    entry_date=entry_date,
                    entry_type='DEBIT',
                    defaults={
                        'amount': Decimal('1000.00'),
                        'description': f'Sample debit entry',
                        'is_posted': True
                    }
                )
                
                # Add credit entries
                LedgerEntry.objects.get_or_create(
                    entity=entity,
                    account=cash_account,
                    entry_date=entry_date,
                    entry_type='CREDIT',
                    defaults={
                        'amount': Decimal('500.00'),
                        'description': f'Sample credit entry',
                        'is_posted': True
                    }
                )
        
        self.stdout.write(self.style.SUCCESS('Sample data added successfully!'))
