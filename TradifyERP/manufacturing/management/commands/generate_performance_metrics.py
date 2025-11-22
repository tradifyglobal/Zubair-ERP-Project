"""
Management command to generate distributor performance metrics for a specific month.
This automates the creation of DistributorPerformance records by calculating metrics
from orders, shipments, and services.
"""

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from datetime import datetime, timedelta
from manufacturing.models import Distributor, DistributorPerformance
from decimal import Decimal


class Command(BaseCommand):
    help = 'Generate distributor performance metrics for a specified month'

    def add_arguments(self, parser):
        parser.add_argument(
            '--year',
            type=int,
            help='Year for performance calculation (default: current year)',
            default=None
        )
        parser.add_argument(
            '--month',
            type=int,
            help='Month for performance calculation (1-12, default: current month)',
            default=None
        )
        parser.add_argument(
            '--distributor-id',
            type=int,
            help='Specific distributor ID (if not provided, calculates for all)',
            default=None
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force overwrite existing records for the month'
        )

    def handle(self, *args, **options):
        # Get year and month
        now = timezone.now()
        year = options.get('year') or now.year
        month = options.get('month') or now.month
        
        # Validate month
        if not (1 <= month <= 12):
            raise CommandError('Month must be between 1 and 12')
        
        self.stdout.write(
            self.style.SUCCESS(f'\n📊 Generating Performance Metrics for {month}/{year}\n')
        )
        
        # Get distributors
        if options['distributor_id']:
            try:
                distributors = Distributor.objects.filter(id=options['distributor_id'])
                if not distributors.exists():
                    raise CommandError(f"Distributor with ID {options['distributor_id']} not found")
            except Distributor.DoesNotExist:
                raise CommandError(f"Distributor with ID {options['distributor_id']} not found")
        else:
            distributors = Distributor.objects.filter(status='ACTIVE')
        
        total_created = 0
        total_updated = 0
        total_errors = 0
        
        self.stdout.write(f'Processing {distributors.count()} distributor(s)...\n')
        
        for distributor in distributors:
            try:
                # Calculate metrics
                metrics = DistributorPerformance.calculate_metrics_for_month(
                    distributor, year, month
                )
                
                # Get first day of month for performance_date
                performance_date = datetime(year, month, 1).date()
                
                # Try to get or create record
                perf_record, created = DistributorPerformance.objects.get_or_create(
                    distributor=distributor,
                    performance_month=month,
                    performance_year=year,
                    defaults={
                        'performance_date': performance_date,
                        'orders_count': metrics['orders_count'],
                        'total_sales': metrics['total_sales'],
                        'average_order_value': metrics['average_order_value'],
                        'on_time_delivery_percentage': metrics['on_time_delivery_percentage'],
                        'order_accuracy_percentage': metrics['order_accuracy_percentage'],
                        'return_rate_percentage': metrics['return_rate_percentage'],
                        'complaint_count': metrics['complaint_count'],
                        'payment_on_time_percentage': metrics['payment_on_time_percentage'],
                        'overall_rating': metrics['overall_rating'],
                    }
                )
                
                if created:
                    total_created += 1
                    status = '✓ CREATED'
                    status_style = self.style.SUCCESS
                else:
                    # Update existing record if force flag is set
                    if options['force']:
                        perf_record.orders_count = metrics['orders_count']
                        perf_record.total_sales = metrics['total_sales']
                        perf_record.average_order_value = metrics['average_order_value']
                        perf_record.on_time_delivery_percentage = metrics['on_time_delivery_percentage']
                        perf_record.order_accuracy_percentage = metrics['order_accuracy_percentage']
                        perf_record.return_rate_percentage = metrics['return_rate_percentage']
                        perf_record.complaint_count = metrics['complaint_count']
                        perf_record.payment_on_time_percentage = metrics['payment_on_time_percentage']
                        perf_record.overall_rating = metrics['overall_rating']
                        perf_record.save()
                        total_updated += 1
                        status = '⟳ UPDATED'
                        status_style = self.style.WARNING
                    else:
                        status = '→ SKIPPED'
                        status_style = self.style.NOTICE
                
                # Print distributor metrics
                self.stdout.write(status_style(
                    f'{status}: {distributor.distributor_name:40} '
                    f'| Orders: {metrics["orders_count"]:3} '
                    f'| Sales: ${metrics["total_sales"]:12.2f} '
                    f'| Rating: {metrics["overall_rating"]}/5'
                ))
                
            except Exception as e:
                total_errors += 1
                self.stdout.write(
                    self.style.ERROR(
                        f'✗ ERROR: {distributor.distributor_name}: {str(e)}'
                    )
                )
        
        # Print summary
        self.stdout.write('\n' + '='*80)
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ Performance metrics generation completed!'
                f'\n  Created: {total_created}'
                f'\n  Updated: {total_updated}'
                f'\n  Skipped: {distributors.count() - total_created - total_updated}'
                f'\n  Errors: {total_errors}\n'
            )
        )


