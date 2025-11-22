"""
Management command for automated monthly performance metric generation.
This should be scheduled to run at the beginning or end of each month.
Can be scheduled via:
  - Cron job: 0 1 1 * * python manage.py auto_generate_performance_metrics
  - Celery Beat
  - Django APScheduler
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from manufacturing.models import Distributor, DistributorPerformance
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Automatically generate performance metrics for the previous month (scheduled task)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--for-current-month',
            action='store_true',
            help='Generate for current month instead of previous month'
        )
        parser.add_argument(
            '--skip-existing',
            action='store_true',
            default=True,
            help='Skip if record already exists (default: True)'
        )

    def handle(self, *args, **options):
        now = timezone.now()
        
        # Determine which month to process
        if options['for_current_month']:
            year = now.year
            month = now.month
            month_desc = "current"
        else:
            # Use previous month
            first_day_this_month = now.replace(day=1)
            last_day_prev_month = first_day_this_month - timedelta(days=1)
            year = last_day_prev_month.year
            month = last_day_prev_month.month
            month_desc = "previous"
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n🤖 Auto-generating performance metrics for {month_desc} month ({month}/{year})\n'
            )
        )
        
        # Get all active distributors
        distributors = Distributor.objects.filter(status='ACTIVE')
        
        if not distributors.exists():
            self.stdout.write(self.style.WARNING('No active distributors found'))
            return
        
        total_created = 0
        total_skipped = 0
        total_errors = 0
        
        for distributor in distributors:
            try:
                # Check if record already exists
                existing = DistributorPerformance.objects.filter(
                    distributor=distributor,
                    performance_month=month,
                    performance_year=year
                ).exists()
                
                if existing and options['skip_existing']:
                    total_skipped += 1
                    continue
                
                # Calculate metrics
                metrics = DistributorPerformance.calculate_metrics_for_month(
                    distributor, year, month
                )
                
                performance_date = datetime(year, month, 1).date()
                
                # Create or update record
                perf_record, created = DistributorPerformance.objects.update_or_create(
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
                    action = '✓ CREATED'
                else:
                    action = '⟳ UPDATED'
                
                self.stdout.write(
                    self.style.SUCCESS(f'{action}: {distributor.distributor_name}')
                )
                
                # Log to application logger
                logger.info(
                    f'Performance metrics {"created" if created else "updated"} for '
                    f'{distributor.distributor_name} ({month}/{year})'
                )
                
            except Exception as e:
                total_errors += 1
                error_msg = f'Error processing {distributor.distributor_name}: {str(e)}'
                self.stdout.write(self.style.ERROR(f'✗ {error_msg}'))
                logger.error(error_msg)
        
        # Print summary
        self.stdout.write('\n' + '='*80)
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ Automated performance generation completed!\n'
                f'  Created: {total_created}\n'
                f'  Skipped: {total_skipped}\n'
                f'  Errors: {total_errors}\n'
            )
        )
