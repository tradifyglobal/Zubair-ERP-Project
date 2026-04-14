"""
Management command to assign report access to users.

Usage:
    python manage.py assign_report_access --username=xyz --report=shareholder_investment --access_level=view_only
    python manage.py assign_report_access --help
"""

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from accounting.models import ReportAccess, Entity
from datetime import datetime, timedelta


class Command(BaseCommand):
    help = 'Assign report access permissions to users'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, help='Username to grant access to')
        parser.add_argument('--user_id', type=int, help='User ID to grant access to')
        parser.add_argument('--report', type=str, help='Report type (e.g., shareholder_investment, accounts)')
        parser.add_argument('--access_level', type=str, default='view_only',
                          help='Access level: view_only, edit, full_access')
        parser.add_argument('--entity', type=str, help='Entity code (optional - leave blank for all entities)')
        parser.add_argument('--expiry_days', type=int, help='Number of days until access expires (optional)')
        parser.add_argument('--list_reports', action='store_true', help='List all available reports')
        parser.add_argument('--list_users', action='store_true', help='List all users')
        parser.add_argument('--remove', action='store_true', help='Remove access (revoke)')

    def handle(self, *args, **options):
        # List available reports
        if options['list_reports']:
            self.list_available_reports()
            return

        # List users
        if options['list_users']:
            self.list_users()
            return

        # Get user
        user = self.get_user(options)
        if not user:
            raise CommandError('Please specify user with --username or --user_id')

        # Get report
        report_type = options.get('report')
        if not report_type:
            raise CommandError('Please specify report with --report')

        # Validate report type
        valid_reports = dict(ReportAccess.REPORT_CHOICES)
        if report_type not in valid_reports:
            raise CommandError(f'Invalid report type: {report_type}. Valid options: {", ".join(valid_reports.keys())}')

        # Get entity if specified
        entity = None
        if options.get('entity'):
            try:
                entity = Entity.objects.get(code=options['entity'])
            except Entity.DoesNotExist:
                raise CommandError(f'Entity not found: {options["entity"]}')

        access_level = options.get('access_level', 'view_only')
        if access_level not in dict(ReportAccess.ACCESS_LEVEL_CHOICES):
            raise CommandError(f'Invalid access level: {access_level}')

        # Remove access if requested
        if options.get('remove'):
            ReportAccess.objects.filter(
                user=user,
                report_type=report_type,
                entity=entity
            ).delete()
            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ Revoked {user.username}\'s access to {report_type}'
                )
            )
            return

        # Create or update access
        expiry_date = None
        if options.get('expiry_days'):
            expiry_date = datetime.now().date() + timedelta(days=options['expiry_days'])

        access, created = ReportAccess.objects.update_or_create(
            user=user,
            report_type=report_type,
            entity=entity,
            defaults={
                'access_level': access_level,
                'is_active': True,
                'expiry_date': expiry_date,
            }
        )

        entity_str = f' for {entity.name}' if entity else ' for all entities'
        action = 'Created' if created else 'Updated'

        self.stdout.write(
            self.style.SUCCESS(
                f'✓ {action} access for {user.username} to {report_type}{entity_str}'
            )
        )
        self.stdout.write(f'  Access level: {access_level}')
        if expiry_date:
            self.stdout.write(f'  Expires: {expiry_date}')

    def get_user(self, options):
        """Get user by username or user_id."""
        if options.get('username'):
            try:
                return User.objects.get(username=options['username'])
            except User.DoesNotExist:
                raise CommandError(f'User not found: {options["username"]}')
        elif options.get('user_id'):
            try:
                return User.objects.get(id=options['user_id'])
            except User.DoesNotExist:
                raise CommandError(f'User not found: ID {options["user_id"]}')
        return None

    def list_available_reports(self):
        """List all available report types."""
        self.stdout.write(self.style.SUCCESS('\n=== Available Reports ===\n'))
        for code, name in ReportAccess.REPORT_CHOICES:
            self.stdout.write(f'  {code:<30} {name}')
        self.stdout.write()

    def list_users(self):
        """List all users."""
        self.stdout.write(self.style.SUCCESS('\n=== Users ===\n'))
        for user in User.objects.all().order_by('username'):
            self.stdout.write(f'  {user.id:<5} {user.username:<20} {user.get_full_name()}')
        self.stdout.write()
