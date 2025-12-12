"""
Management command to create Django Groups for Capital Contribution workflow.
Usage: python manage.py setup_contribution_groups
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from accounting.models import CapitalContribution


class Command(BaseCommand):
    help = 'Create Django Groups for Capital Contribution reviewers and approvers'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Delete existing groups and recreate',
        )

    def handle(self, *args, **options):
        group_names = [
            'Capital Contribution Reviewers',
            'Capital Contribution Approvers'
        ]

        if options['reset']:
            Group.objects.filter(name__in=group_names).delete()
            self.stdout.write(self.style.WARNING('Deleted existing Capital Contribution groups'))

        # Get or create the groups
        reviewer_group, created = Group.objects.get_or_create(
            name='Capital Contribution Reviewers'
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Created group: {reviewer_group.name}'))
        else:
            self.stdout.write(self.style.WARNING(f'○ Group already exists: {reviewer_group.name}'))

        approver_group, created = Group.objects.get_or_create(
            name='Capital Contribution Approvers'
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Created group: {approver_group.name}'))
        else:
            self.stdout.write(self.style.WARNING(f'○ Group already exists: {approver_group.name}'))

        # Get ContentType for CapitalContribution
        try:
            content_type = ContentType.objects.get_for_model(CapitalContribution)
            
            # Get relevant permissions
            view_perm = Permission.objects.get(
                content_type=content_type,
                codename='view_capitalcontribution'
            )
            change_perm = Permission.objects.get(
                content_type=content_type,
                codename='change_capitalcontribution'
            )
            
            # Assign permissions to reviewer group
            reviewer_group.permissions.add(view_perm, change_perm)
            self.stdout.write(self.style.SUCCESS(
                f'  → Added view and change permissions to {reviewer_group.name}'
            ))
            
            # Assign permissions to approver group
            approver_group.permissions.add(view_perm, change_perm)
            self.stdout.write(self.style.SUCCESS(
                f'  → Added view and change permissions to {approver_group.name}'
            ))
            
        except Permission.DoesNotExist:
            self.stdout.write(self.style.ERROR(
                'Could not find permissions for CapitalContribution model. '
                'Make sure migrations are applied.'
            ))

        self.stdout.write('\n' + self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('Setup Complete!'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write('\nNext Steps:')
        self.stdout.write('1. Add users to "Capital Contribution Reviewers" group in Django Admin')
        self.stdout.write('2. Add users to "Capital Contribution Approvers" group in Django Admin')
        self.stdout.write('3. Any user in the Reviewers group can review contributions')
        self.stdout.write('4. Any user in the Approvers group can approve contributions\n')
