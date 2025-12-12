"""
Management command to generate trial balance.

Usage:
    python manage.py generate_trial_balance
    python manage.py generate_trial_balance --entity=ABC --date=2025-12-10
"""

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from datetime import datetime, date
from decimal import Decimal
from accounting.models import Entity, TrialBalance
from accounting.trial_balance import calculate_trial_balance, save_trial_balance, verify_gl_balance


class Command(BaseCommand):
    help = 'Generate trial balance from GL entries'

    def add_arguments(self, parser):
        parser.add_argument(
            '--entity',
            type=str,
            help='Entity code (e.g., ABC). If not provided, processes all entities.',
        )
        parser.add_argument(
            '--date',
            type=str,
            help='As-of date in YYYY-MM-DD format. Defaults to today.',
        )
        parser.add_argument(
            '--verify-only',
            action='store_true',
            help='Only verify GL balance without saving.',
        )

    def handle(self, *args, **options):
        entity_code = options.get('entity')
        date_str = options.get('date')
        verify_only = options.get('verify_only', False)

        # Parse date
        if date_str:
            try:
                as_of_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                raise CommandError(
                    'Invalid date format. Use YYYY-MM-DD (e.g., 2025-12-10)'
                )
        else:
            as_of_date = date.today()

        # Get entities
        if entity_code:
            try:
                entities = [Entity.objects.get(code=entity_code)]
            except Entity.DoesNotExist:
                raise CommandError(f'Entity with code "{entity_code}" not found')
        else:
            entities = Entity.objects.filter(is_active=True)

        if not entities:
            raise CommandError('No active entities found')

        self.stdout.write(
            self.style.SUCCESS(
                f'Processing {len(entities)} entity/entities as of {as_of_date}'
            )
        )
        self.stdout.write('-' * 80)

        for entity in entities:
            self.stdout.write(f'\nProcessing: {entity.code} ({entity.name})')

            try:
                # Calculate trial balance
                tb_data = calculate_trial_balance(entity, as_of_date)

                if 'error' in tb_data:
                    self.stdout.write(
                        self.style.ERROR(f'  Error: {tb_data["error"]}')
                    )
                    continue

                total_debits = tb_data['total_debits']
                total_credits = tb_data['total_credits']
                is_balanced = tb_data['is_balanced']
                accounts = tb_data['account_balances']

                # Display results
                self.stdout.write(f'  Total Debits:  {total_debits:>15,.2f}')
                self.stdout.write(f'  Total Credits: {total_credits:>15,.2f}')
                self.stdout.write(
                    self.style.SUCCESS('  Status: BALANCED')
                    if is_balanced
                    else self.style.ERROR('  Status: OUT OF BALANCE')
                )

                # Show accounts with balances
                if accounts:
                    self.stdout.write(f'\n  Account Balances ({len(accounts)} accounts):')
                    self.stdout.write('  ' + '-' * 76)
                    self.stdout.write(
                        '  {:<6} {:<40} {:<12} {:<12}'.format(
                            'Code', 'Account Name', 'Debits', 'Credits'
                        )
                    )
                    self.stdout.write('  ' + '-' * 76)

                    for account_bal in accounts:
                        code = account_bal['account_number']
                        name = account_bal['account_name'][:38]
                        debits = account_bal['debit_balance']
                        credits = account_bal['credit_balance']

                        self.stdout.write(
                            '  {:<6} {:<40} ${:>10,.2f} ${:>10,.2f}'.format(
                                code, name, debits, credits
                            )
                        )

                # Save to database if not verify-only
                if not verify_only:
                    saved_tb = save_trial_balance(entity, as_of_date)
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'  Saved Trial Balance (ID: {saved_tb.id})'
                        )
                    )

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'  Failed to process: {str(e)}')
                )

        self.stdout.write('\n' + '=' * 80)
        self.stdout.write(self.style.SUCCESS('Trial balance generation complete!'))
