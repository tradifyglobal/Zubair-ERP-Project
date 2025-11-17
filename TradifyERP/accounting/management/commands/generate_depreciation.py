from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from accounting.models import FixedAsset, LedgerEntry, Account, Entity


class Command(BaseCommand):
    help = 'Generate monthly depreciation entries for fixed assets'

    def add_arguments(self, parser):
        parser.add_argument(
            '--entity-id',
            type=int,
            help='Generate depreciation for a specific entity',
        )
        parser.add_argument(
            '--year-month',
            type=str,
            help='Generate depreciation for specific year-month (YYYY-MM)',
        )

    def handle(self, *args, **options):
        entity_id = options.get('entity_id')
        year_month = options.get('year_month')
        
        # Get current date or specified date
        if year_month:
            try:
                year, month = year_month.split('-')
                depreciation_date = timezone.make_aware(
                    timezone.datetime(int(year), int(month), 1)
                )
            except (ValueError, AttributeError):
                self.stdout.write(self.style.ERROR('Invalid year-month format. Use YYYY-MM'))
                return
        else:
            # Default to last day of previous month
            today = timezone.now().date()
            depreciation_date = timezone.make_aware(
                timezone.datetime(today.year, today.month, 1) - timedelta(days=1)
            )
        
        # Filter entities
        if entity_id:
            entities = Entity.objects.filter(id=entity_id)
        else:
            entities = Entity.objects.filter(is_active=True)
        
        total_entries_created = 0
        
        for entity in entities:
            self.stdout.write(f'\nProcessing entity: {entity.name}')
            
            # Get all active fixed assets that haven't been disposed
            assets = FixedAsset.objects.filter(
                entity=entity,
                is_active=True,
                is_disposed=False
            )
            
            # Find or create Accumulated Depreciation account
            accum_depr_account = Account.objects.filter(
                entity=entity,
                account_type='ASSET',
                name__icontains='accumulated depreciation'
            ).first()
            
            if not accum_depr_account:
                currency = entity.accounts.filter(is_active=True).values_list('currency', flat=True).first()
                from accounting.models import Currency
                if not currency:
                    currency_obj = Currency.objects.filter(is_active=True).first()
                else:
                    currency_obj = Currency.objects.get(id=currency)
                
                accum_depr_account = Account.objects.create(
                    entity=entity,
                    account_number='1510',
                    name='Accumulated Depreciation',
                    account_type='ASSET',
                    currency=currency_obj,
                    description='Accumulated Depreciation - Contra Asset Account'
                )
            
            # Find or create Depreciation Expense account
            depr_expense_account = Account.objects.filter(
                entity=entity,
                account_type='EXPENSE',
                name__icontains='depreciation'
            ).first()
            
            if not depr_expense_account:
                currency_obj = accum_depr_account.currency
                depr_expense_account = Account.objects.create(
                    entity=entity,
                    account_number='5100',
                    name='Depreciation Expense',
                    account_type='EXPENSE',
                    currency=currency_obj,
                    description='Depreciation Expense Account'
                )
            
            # Generate depreciation for each asset
            for asset in assets:
                # Check if depreciation already exists for this month
                existing_entries = LedgerEntry.objects.filter(
                    account=depr_expense_account,
                    entity=entity,
                    entry_date__year=depreciation_date.year,
                    entry_date__month=depreciation_date.month,
                    description__contains=asset.asset_code
                ).exists()
                
                if existing_entries:
                    self.stdout.write(
                        self.style.WARNING(
                            f'  Depreciation already recorded for {asset.name} in {depreciation_date.strftime("%Y-%m")}'
                        )
                    )
                    continue
                
                # Check if asset purchase date is before depreciation date
                if asset.purchase_date > depreciation_date.date():
                    self.stdout.write(
                        self.style.WARNING(
                            f'  Asset {asset.name} purchased after depreciation date. Skipping.'
                        )
                    )
                    continue
                
                # Calculate monthly depreciation
                monthly_depreciation = asset.get_monthly_depreciation()
                
                if monthly_depreciation <= 0:
                    continue
                
                # Create depreciation entries (Dr. Depreciation Expense / Cr. Accumulated Depreciation)
                debit_entry = LedgerEntry.objects.create(
                    account=depr_expense_account,
                    entity=entity,
                    entry_date=depreciation_date.date(),
                    entry_type='DEBIT',
                    amount=monthly_depreciation,
                    description=f'Depreciation expense for {asset.name} ({asset.asset_code}) - {depreciation_date.strftime("%b %Y")}',
                    reference_number=f'DEP-{asset.asset_code}-{depreciation_date.strftime("%Y%m")}',
                    is_posted=True
                )
                
                credit_entry = LedgerEntry.objects.create(
                    account=accum_depr_account,
                    entity=entity,
                    entry_date=depreciation_date.date(),
                    entry_type='CREDIT',
                    amount=monthly_depreciation,
                    description=f'Accumulated depreciation for {asset.name} ({asset.asset_code}) - {depreciation_date.strftime("%b %Y")}',
                    reference_number=f'DEP-{asset.asset_code}-{depreciation_date.strftime("%Y%m")}',
                    is_posted=True
                )
                
                # Update asset's accumulated depreciation and book value
                asset.accumulated_depreciation += monthly_depreciation
                asset.book_value = asset.purchase_cost - asset.accumulated_depreciation
                asset.last_depreciation_date = depreciation_date.date()
                asset.save()
                
                total_entries_created += 2
                self.stdout.write(
                    self.style.SUCCESS(
                        f'  ✓ Created depreciation entry for {asset.name}: {monthly_depreciation}'
                    )
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n\nTotal ledger entries created: {total_entries_created}'
            )
        )
