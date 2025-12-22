"""
Management command to setup standard GL accounts for a given entity.
Usage: python manage.py setup_standard_accounts --entity INT-001
Or: python manage.py setup_standard_accounts (uses all entities)
"""

from django.core.management.base import BaseCommand
from accounting.models import Entity, Account, Currency


class Command(BaseCommand):
    help = 'Setup standard GL accounts (Chart of Accounts) for entities'

    def add_arguments(self, parser):
        parser.add_argument(
            '--entity',
            type=str,
            help='Entity code (e.g., INT-001). If not provided, setup all entities.',
        )
        parser.add_argument(
            '--skip-cash',
            action='store_true',
            help='Skip creating Cash account (100001)',
        )

    def handle(self, *args, **options):
        entity_code = options.get('entity')
        skip_cash = options.get('skip_cash', False)

        if entity_code:
            try:
                entities = [Entity.objects.get(code=entity_code)]
                self.stdout.write(
                    self.style.SUCCESS(f'Setting up accounts for entity: {entity_code}')
                )
            except Entity.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Entity {entity_code} not found')
                )
                return
        else:
            entities = Entity.objects.all()
            self.stdout.write(
                self.style.SUCCESS(f'Setting up accounts for {entities.count()} entities')
            )

        # Get default currency (INR)
        try:
            inr_currency = Currency.objects.get(code='INR')
        except Currency.DoesNotExist:
            self.stdout.write(
                self.style.ERROR('Currency INR not found. Please create it first.')
            )
            return

        # Standard accounts to create
        standard_accounts = [
            {
                'account_number': '1000',
                'name': 'Assets',
                'type': 'ASSET',
                'description': 'Asset accounts',
                'parent': None,
            },
            {
                'account_number': '1100',
                'name': 'Cash and Bank',
                'type': 'ASSET',
                'description': 'Cash and bank accounts',
                'parent': '1000',
            },
            {
                'account_number': '100001',
                'name': 'Cash',
                'type': 'ASSET',
                'description': 'Cash account for receiving cash from shareholders',
                'parent': '1100',
            },
            {
                'account_number': '3000',
                'name': 'Capital',
                'type': 'EQUITY',
                'description': 'Shareholder capital accounts',
                'parent': None,
            },
            {
                'account_number': '3100',
                'name': 'Capital',
                'type': 'EQUITY',
                'description': 'Shareholder Investment',
                'parent': '3000',
            },
            {
                'account_number': '4000',
                'name': 'Income',
                'type': 'INCOME',
                'description': 'Income accounts',
                'parent': None,
            },
            {
                'account_number': '5000',
                'name': 'Expenses',
                'type': 'EXPENSE',
                'description': 'Expense accounts',
                'parent': None,
            },
        ]

        if skip_cash:
            standard_accounts = [acc for acc in standard_accounts if acc['account_number'] != '100001']

        created_count = 0
        skipped_count = 0

        for entity in entities:
            for acc_data in standard_accounts:
                # Get parent account if specified
                parent_account = None
                if acc_data['parent']:
                    try:
                        parent_account = Account.objects.get(
                            entity=entity,
                            account_number=acc_data['parent']
                        )
                    except Account.DoesNotExist:
                        self.stdout.write(
                            self.style.WARNING(
                                f"Parent account {acc_data['parent']} not found for {entity.code}, skipping {acc_data['account_number']}"
                            )
                        )
                        skipped_count += 1
                        continue

                # Create or skip if exists
                account, created = Account.objects.get_or_create(
                    entity=entity,
                    account_number=acc_data['account_number'],
                    defaults={
                        'name': acc_data['name'],
                        'account_type': acc_data['type'],
                        'description': acc_data['description'],
                        'currency': inr_currency,
                        'is_active': True,
                        'opening_balance': 0.00,
                        'parent_account': parent_account,
                    }
                )

                if created:
                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Created: {entity.code} - {acc_data['account_number']} ({acc_data['name']})"
                        )
                    )
                else:
                    skipped_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'\nSetup complete! Created: {created_count}, Skipped (already exist): {skipped_count}'
            )
        )
