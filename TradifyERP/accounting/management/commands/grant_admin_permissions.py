"""
Management command to grant Django admin permissions to all staff users.
This syncs module permissions with Django's built-in admin permissions.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

User = get_user_model()


class Command(BaseCommand):
    help = 'Grants all Django admin permissions to staff users'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user',
            type=str,
            help='Username to grant permissions to (if not specified, applies to all staff)',
        )

    def handle(self, *args, **options):
        username = options.get('user')
        
        if username:
            try:
                users = [User.objects.get(username=username)]
                self.stdout.write(f'Granting permissions to user: {username}')
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'User "{username}" not found')
                )
                return
        else:
            users = User.objects.filter(is_staff=True, is_superuser=False)
            self.stdout.write(f'Granting permissions to {users.count()} staff user(s)')
        
        # Get all permissions
        all_permissions = Permission.objects.all()
        
        for user in users:
            # Clear existing permissions
            user.user_permissions.clear()
            
            # Grant all permissions
            user.user_permissions.set(all_permissions)
            
            self.stdout.write(
                self.style.SUCCESS(f'  ✓ Granted {all_permissions.count()} permissions to {user.username}')
            )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ Successfully granted admin permissions to {len(users)} user(s)'
            )
        )
        
        self.stdout.write(
            self.style.WARNING(
                '\nNote: Users now have Django admin permissions.'
            )
        )
        self.stdout.write(
            self.style.WARNING(
                'Frontend access is still controlled by module permissions.'
            )
        )
