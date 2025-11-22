"""
Management command to set is_staff=True for all users.
This enables admin site access which is required for templates using admin URLs.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Sets is_staff=True for all non-superuser users to enable admin access'

    def handle(self, *args, **options):
        # Update all users who are not superusers to have staff status
        updated_count = User.objects.filter(
            is_staff=False,
            is_superuser=False
        ).update(is_staff=True)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'✓ Updated {updated_count} user(s) to have staff status'
            )
        )
        
        # Display summary
        total_staff = User.objects.filter(is_staff=True).count()
        total_superusers = User.objects.filter(is_superuser=True).count()
        total_users = User.objects.count()
        
        self.stdout.write(f'\nSummary:')
        self.stdout.write(f'  Total users: {total_users}')
        self.stdout.write(f'  Staff users: {total_staff}')
        self.stdout.write(f'  Superusers: {total_superusers}')
        
        self.stdout.write(
            self.style.WARNING(
                '\nNote: All users now have staff status to access admin pages.'
            )
        )
        self.stdout.write(
            self.style.WARNING(
                'Access is still controlled by module permissions.'
            )
        )
