"""
Management command to assign users to entities.

Usage:
    python manage.py assign_user_to_entity <username> <entity_code> [--default] [--can-switch]
    
Examples:
    # Assign user to single entity as default
    python manage.py assign_user_to_entity burhan PP-01 --default
    
    # Assign user to entity and allow switching
    python manage.py assign_user_to_entity burhan MAIN --can-switch
    
    # Assign user to multiple entities
    python manage.py assign_user_to_entity burhan PP-01
    python manage.py assign_user_to_entity burhan MAIN --default
"""

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from accounting.models import Entity, UserEntity


class Command(BaseCommand):
    help = 'Assign a user to one or more entities'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username of the user to assign')
        parser.add_argument('entity_code', type=str, help='Code of the entity to assign (e.g., MAIN, PP-01)')
        parser.add_argument(
            '--default',
            action='store_true',
            help='Set this as the user\'s default entity'
        )
        parser.add_argument(
            '--can-switch',
            action='store_true',
            help='Allow user to switch to other assigned entities'
        )
        parser.add_argument(
            '--remove',
            action='store_true',
            help='Remove user from this entity instead of assigning'
        )

    def handle(self, *args, **options):
        username = options['username']
        entity_code = options['entity_code']
        
        # Get user
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise CommandError(f'User "{username}" not found')
        
        # Get entity
        try:
            entity = Entity.objects.get(code=entity_code)
        except Entity.DoesNotExist:
            raise CommandError(f'Entity with code "{entity_code}" not found')
        
        if options['remove']:
            # Remove user from entity
            try:
                user_entity = UserEntity.objects.get(user=user, entity=entity)
                user_entity.delete()
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ Removed {user.username} from {entity.code}'
                    )
                )
            except UserEntity.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(
                        f'User "{username}" is not assigned to entity "{entity_code}"'
                    )
                )
        else:
            # Assign user to entity
            if options['default']:
                # If setting as default, unset any other defaults for this user
                UserEntity.objects.filter(user=user).update(is_default=False)
            
            user_entity, created = UserEntity.objects.get_or_create(
                user=user,
                entity=entity,
                defaults={
                    'is_default': options['default'],
                    'can_switch': options['can_switch'],
                    'assigned_by': user  # Use the same user or an admin user
                }
            )
            
            if not created:
                # Update existing assignment
                user_entity.is_default = options['default']
                user_entity.can_switch = options['can_switch']
                user_entity.save()
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ Updated {user.username} entity assignment for {entity.code}'
                    )
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ Assigned {user.username} to {entity.code}'
                    )
                )
            
            # Print current assignments
            assignments = UserEntity.objects.filter(user=user).select_related('entity')
            self.stdout.write(self.style.SUCCESS(f'\n  Current assignments for {user.username}:'))
            for assignment in assignments:
                default_marker = ' [DEFAULT]' if assignment.is_default else ''
                switch_marker = ' [CAN_SWITCH]' if assignment.can_switch else ' [NO_SWITCH]'
                self.stdout.write(f'    - {assignment.entity.code} {default_marker}{switch_marker}')
