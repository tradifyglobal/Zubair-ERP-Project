"""
Management command to initialize RBAC system with 7 standard financial roles.
Usage: python manage.py setup_roles
"""

from django.core.management.base import BaseCommand
from accounting.role_models import Role
from django.contrib.auth.models import Group


class Command(BaseCommand):
    help = 'Initialize 7 standard financial roles for SOX 302/404 compliance'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Delete existing roles and recreate',
        )

    def handle(self, *args, **options):
        if options['reset']:
            Role.objects.all().delete()
            self.stdout.write(self.style.WARNING('Deleted existing roles'))

        roles_data = [
            {
                'name': 'Accountant',
                'description': 'Data entry clerk - creates GL entries',
                'hierarchy_level': 0,
                'can_create': True,
                'can_read': True,
                'can_update': False,
                'can_delete': False,
                'can_approve': False,
                'can_post': False,
                'can_export': False,
            },
            {
                'name': 'Supervisor',
                'description': 'Supervises accounting entries - approves and reviews',
                'hierarchy_level': 1,
                'can_create': True,
                'can_read': True,
                'can_update': True,
                'can_delete': False,
                'can_approve': True,
                'can_post': False,
                'can_export': False,
            },
            {
                'name': 'Controller',
                'description': 'Controls GL posting - posts approved entries',
                'hierarchy_level': 2,
                'can_create': True,
                'can_read': True,
                'can_update': True,
                'can_delete': False,
                'can_approve': True,
                'can_post': True,
                'can_export': False,
            },
            {
                'name': 'Financial Manager',
                'description': 'Financial reporting and analysis',
                'hierarchy_level': 3,
                'can_create': True,
                'can_read': True,
                'can_update': True,
                'can_delete': False,
                'can_approve': True,
                'can_post': True,
                'can_export': True,
            },
            {
                'name': 'Finance Director',
                'description': 'Approves financial statements and major transactions',
                'hierarchy_level': 4,
                'can_create': True,
                'can_read': True,
                'can_update': True,
                'can_delete': True,
                'can_approve': True,
                'can_post': True,
                'can_export': True,
            },
            {
                'name': 'CFO',
                'description': 'Chief Financial Officer - final approvals and certifications',
                'hierarchy_level': 5,
                'can_create': True,
                'can_read': True,
                'can_update': True,
                'can_delete': True,
                'can_approve': True,
                'can_post': True,
                'can_export': True,
            },
            {
                'name': 'Auditor',
                'description': 'Internal/External auditor - read-only access',
                'hierarchy_level': 6,
                'can_create': False,
                'can_read': True,
                'can_update': False,
                'can_delete': False,
                'can_approve': False,
                'can_post': False,
                'can_export': True,
            },
        ]

        created_count = 0
        for role_data in roles_data:
            role, created = Role.objects.get_or_create(
                name=role_data['name'],
                defaults=role_data
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created role: {role.name} (level {role.hierarchy_level})')
                )
                created_count += 1
            else:
                self.stdout.write(f'→ Role already exists: {role.name}')

        self.stdout.write(
            self.style.SUCCESS(f'\n✓ Setup complete: {created_count} new roles created')
        )
