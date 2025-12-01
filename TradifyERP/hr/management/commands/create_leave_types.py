"""
Management command to create default leave types for all entities.
"""
from django.core.management.base import BaseCommand
from accounting.models import Entity
from hr.models import Leave
from django.utils import timezone


class Command(BaseCommand):
    help = 'Create default leave types for all entities'

    def handle(self, *args, **options):
        leave_types = [
            {
                'name': 'Annual Leave',
                'code': 'AL',
                'annual_allocation': 20,
                'accrual_method': 'ANNUAL',
                'can_carry_over': True,
                'max_carryover': 5,
                'requires_approval': True,
                'notice_days_required': 7,
                'description': 'Annual/Vacation leave for employees'
            },
            {
                'name': 'Sick Leave',
                'code': 'SL',
                'annual_allocation': 10,
                'accrual_method': 'MONTHLY',
                'can_carry_over': True,
                'max_carryover': 3,
                'requires_approval': True,
                'notice_days_required': 1,
                'description': 'Leave for medical emergencies and illness'
            },
            {
                'name': 'Casual Leave',
                'code': 'CL',
                'annual_allocation': 8,
                'accrual_method': 'QUARTERLY',
                'can_carry_over': False,
                'max_carryover': 0,
                'requires_approval': True,
                'notice_days_required': 3,
                'description': 'Casual leave for personal reasons'
            },
            {
                'name': 'Maternity Leave',
                'code': 'ML',
                'annual_allocation': 180,
                'accrual_method': 'ANNUAL',
                'can_carry_over': False,
                'max_carryover': 0,
                'requires_approval': True,
                'notice_days_required': 30,
                'description': 'Maternity leave for female employees'
            },
            {
                'name': 'Paternity Leave',
                'code': 'PL',
                'annual_allocation': 10,
                'accrual_method': 'ANNUAL',
                'can_carry_over': False,
                'max_carryover': 0,
                'requires_approval': True,
                'notice_days_required': 30,
                'description': 'Paternity leave for male employees'
            },
            {
                'name': 'Bereavement Leave',
                'code': 'BL',
                'annual_allocation': 5,
                'accrual_method': 'ANNUAL',
                'can_carry_over': False,
                'max_carryover': 0,
                'requires_approval': True,
                'notice_days_required': 0,
                'description': 'Leave for death in the family'
            },
            {
                'name': 'Marriage Leave',
                'code': 'MR',
                'annual_allocation': 3,
                'accrual_method': 'ANNUAL',
                'can_carry_over': False,
                'max_carryover': 0,
                'requires_approval': True,
                'notice_days_required': 30,
                'description': 'Leave for personal marriage'
            },
            {
                'name': 'Unpaid Leave',
                'code': 'UL',
                'annual_allocation': 0,
                'accrual_method': 'ANNUAL',
                'can_carry_over': False,
                'max_carryover': 0,
                'requires_approval': True,
                'notice_days_required': 15,
                'description': 'Unpaid leave at employee request'
            },
            {
                'name': 'Study/Exam Leave',
                'code': 'EL',
                'annual_allocation': 5,
                'accrual_method': 'ANNUAL',
                'can_carry_over': False,
                'max_carryover': 0,
                'requires_approval': True,
                'notice_days_required': 7,
                'description': 'Leave for educational examinations'
            },
            {
                'name': 'Compensatory Off (Comp-Off)',
                'code': 'CO',
                'annual_allocation': 0,
                'accrual_method': 'ANNUAL',
                'can_carry_over': True,
                'max_carryover': 5,
                'requires_approval': True,
                'notice_days_required': 1,
                'description': 'Extra leave for overtime work'
            },
        ]

        # Get all entities
        entities = Entity.objects.all()
        
        if not entities.exists():
            self.stdout.write(self.style.WARNING('No entities found. Please create entities first.'))
            return

        created_count = 0
        skipped_count = 0

        for entity in entities:
            for leave_data in leave_types:
                # Check if this leave type already exists for this entity
                leave, created = Leave.objects.get_or_create(
                    entity=entity,
                    code=leave_data['code'],
                    defaults={
                        'name': leave_data['name'],
                        'annual_allocation': leave_data['annual_allocation'],
                        'accrual_method': leave_data['accrual_method'],
                        'can_carry_over': leave_data['can_carry_over'],
                        'max_carryover': leave_data['max_carryover'],
                        'requires_approval': leave_data['requires_approval'],
                        'notice_days_required': leave_data['notice_days_required'],
                        'status': 'APPROVED',  # Auto-approve all default leave types
                        'approved_by': None,  # System approved
                        'approval_date': timezone.now(),
                    }
                )
                
                if created:
                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'✓ Created: {leave_data["name"]} for {entity.name}'
                        )
                    )
                else:
                    skipped_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ Complete! Created {created_count} leave types, Skipped {skipped_count} (already exist)'
            )
        )
