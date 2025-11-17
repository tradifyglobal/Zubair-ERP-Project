"""
Management command to setup GL accounts for Sales module.
Run: python manage.py setup_sales_gl_accounts [entity_code]
"""

from django.core.management.base import BaseCommand
from accounting.models import Entity, Account, Currency
from decimal import Decimal


class Command(BaseCommand):
    help = 'Create GL accounts required for Sales module accounting'
    
    def add_arguments(self, parser):
        parser.add_argument(
            'entity_code',
            type=str,
            nargs='?',
            default=None,
            help='Entity code to setup GL accounts for. If not provided, setup for all entities.'
        )
    
    def handle(self, *args, **options):
        entity_code = options['entity_code']
        
        # Get entities
        if entity_code:
            try:
                entities = [Entity.objects.get(code=entity_code)]
            except Entity.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Entity with code {entity_code} not found'))
                return
        else:
            entities = Entity.objects.filter(is_active=True)
        
        # Get or create default currency (USD)
        currency, _ = Currency.objects.get_or_create(
            code='USD',
            defaults={
                'name': 'US Dollar',
                'symbol': '$',
                'exchange_rate': Decimal('1.0'),
                'is_active': True
            }
        )
        
        gl_accounts_created = 0
        
        # Define GL accounts needed for Sales module
        # Chart of Accounts structure
        accounts_to_create = [
            # ASSET accounts
            {
                'account_number': '1200',
                'name': 'Accounts Receivable',
                'account_type': 'ASSET',
                'description': 'Customer invoices not yet paid'
            },
            {
                'account_number': '1000',
                'name': 'Cash',
                'account_type': 'ASSET',
                'description': 'Cash and bank accounts'
            },
            # LIABILITY accounts
            {
                'account_number': '2110',
                'name': 'Sales Tax Payable',
                'account_type': 'LIABILITY',
                'description': 'Sales tax collected from customers'
            },
            # INCOME accounts
            {
                'account_number': '4100',
                'name': 'Sales Revenue',
                'account_type': 'INCOME',
                'description': 'Revenue from product and service sales'
            },
            {
                'account_number': '4200',
                'name': 'Sales Discounts',
                'account_type': 'INCOME',
                'description': 'Discounts given to customers (contra-revenue)'
            },
            # EXPENSE accounts (for refunds/returns)
            {
                'account_number': '5100',
                'name': 'Cost of Goods Sold',
                'account_type': 'EXPENSE',
                'description': 'Cost of goods sold to customers'
            },
        ]
        
        for entity in entities:
            self.stdout.write(f'\nSetting up GL accounts for entity: {entity.code} - {entity.name}')
            
            for account_data in accounts_to_create:
                try:
                    account, created = Account.objects.get_or_create(
                        entity=entity,
                        account_number=account_data['account_number'],
                        defaults={
                            'name': account_data['name'],
                            'account_type': account_data['account_type'],
                            'description': account_data['description'],
                            'currency': currency,
                            'is_active': True,
                            'opening_balance': Decimal('0.00')
                        }
                    )
                    
                    if created:
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'  ✓ Created: {account.account_number} - {account.name}'
                            )
                        )
                        gl_accounts_created += 1
                    else:
                        self.stdout.write(
                            f'  ○ Already exists: {account.account_number} - {account.name}'
                        )
                
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f'  ✗ Error creating {account_data["account_number"]}: {str(e)}'
                        )
                    )
        
        self.stdout.write(
            self.style.SUCCESS(f'\n✓ Setup complete! Created {gl_accounts_created} new GL accounts.')
        )
        self.stdout.write(
            self.style.WARNING(
                '\nNext steps:\n'
                '1. Verify accounts in the Accounting module GL chart\n'
                '2. Create invoices and watch GL entries appear automatically\n'
                '3. View ledger entries in Accounting > Ledger\n'
                '4. Check P&L reports in Accounting > Reports'
            )
        )
