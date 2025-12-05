"""
Management command to list user entity assignments.

Usage:
    python manage.py list_user_entities [username]
    
Examples:
    # List all user entity assignments
    python manage.py list_user_entities
    
    # List assignments for specific user
    python manage.py list_user_entities burhan
"""

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from accounting.models import UserEntity


class Command(BaseCommand):
    help = 'List user entity assignments'

    def add_arguments(self, parser):
        parser.add_argument(
            'username',
            type=str,
            nargs='?',
            help='Username to list entities for (optional)'
        )

    def handle(self, *args, **options):
        username = options.get('username')
        
        if username:
            # List assignments for specific user
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                raise CommandError(f'User "{username}" not found')
            
            assignments = UserEntity.objects.filter(user=user).select_related('entity', 'assigned_by')
            
            if not assignments.exists():
                self.stdout.write(
                    self.style.WARNING(
                        f'⚠️  User "{username}" has NO entity assignments'
                    )
                )
                return
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'\n📋 Entity Assignments for {user.get_full_name() or username} ({user.username})\n'
                )
            )
            
            for assignment in assignments:
                default_marker = self.style.SUCCESS('✓ DEFAULT') if assignment.is_default else ''
                switch_marker = self.style.SUCCESS('CAN_SWITCH') if assignment.can_switch else self.style.ERROR('NO_SWITCH')
                assigned_by = f' (assigned by {assignment.assigned_by.username})' if assignment.assigned_by else ''
                
                self.stdout.write(
                    f'  {assignment.entity.code:12} {assignment.entity.name:25} {default_marker:15} {switch_marker}{assigned_by}'
                )
            
            self.stdout.write('')
        else:
            # List all assignments grouped by user
            users_with_entities = User.objects.filter(
                entity_assignments__isnull=False
            ).distinct().order_by('username')
            
            users_without_entities = User.objects.exclude(
                pk__in=UserEntity.objects.values_list('user_id', flat=True)
            ).filter(is_active=True).order_by('username')
            
            if users_with_entities.exists():
                self.stdout.write(
                    self.style.SUCCESS(
                        '\n📋 Users WITH Entity Assignments:\n'
                    )
                )
                for user in users_with_entities:
                    assignments = UserEntity.objects.filter(user=user).select_related('entity')
                    entities_str = ', '.join([
                        f'{a.entity.code}{"*" if a.is_default else ""}'
                        for a in assignments
                    ])
                    self.stdout.write(f'  {user.username:20} → {entities_str}')
            
            if users_without_entities.exists():
                self.stdout.write(
                    self.style.WARNING(
                        f'\n⚠️  Users WITHOUT Entity Assignments ({users_without_entities.count()}):\n'
                    )
                )
                for user in users_without_entities:
                    self.stdout.write(f'  {user.username:20} (needs assignment)')
            
            self.stdout.write('')
