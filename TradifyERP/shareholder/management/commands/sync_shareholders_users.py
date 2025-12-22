"""
Management command to sync existing shareholders with user accounts.
Creates users for all shareholders that don't have corresponding user accounts.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounting.models import Stakeholder, UserEntity
from accounting.module_permissions import ModulePermission
import logging
import secrets
import string

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Sync existing shareholders with user accounts. Creates users for shareholders without user accounts.'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without making changes',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed output',
        )
    
    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)
        verbose = options.get('verbose', False)
        
        self.stdout.write(self.style.SUCCESS('\n=== Shareholder-User Sync ===\n'))
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made\n'))
        
        # Get all stakeholders
        all_stakeholders = Stakeholder.objects.all().order_by('id')
        self.stdout.write(f'Total shareholders in system: {all_stakeholders.count()}')
        
        # Get all users
        all_users = User.objects.all()
        self.stdout.write(f'Total users in system: {all_users.count()}')
        
        # Find stakeholders without users
        created_count = 0
        updated_count = 0
        skipped_count = 0
        error_count = 0
        
        self.stdout.write('\n--- Processing Shareholders ---\n')
        
        for stakeholder in all_stakeholders:
            email = stakeholder.email
            
            if not email:
                if verbose:
                    self.stdout.write(self.style.WARNING(
                        f'SKIP: Stakeholder {stakeholder.id} - No email provided'
                    ))
                skipped_count += 1
                continue
            
            # Check if user exists
            try:
                existing_user = User.objects.get(email=email)
                
                # Update existing user
                if verbose:
                    self.stdout.write(f'UPDATE: User {existing_user.username} ({email})')
                
                if not dry_run:
                    if stakeholder.stakeholder_type == 'INDIVIDUAL':
                        existing_user.first_name = (stakeholder.first_name or '')[:150]
                        existing_user.last_name = (stakeholder.last_name or '')[:150]
                    else:
                        existing_user.first_name = (stakeholder.company_name or '')[:150]
                        existing_user.last_name = ''
                    
                    existing_user.save()
                
                updated_count += 1
                
            except User.DoesNotExist:
                # Create new user
                try:
                    # Generate username
                    username_base = email.split('@')[0]
                    username = username_base
                    counter = 1
                    while User.objects.filter(username=username).exists():
                        username = f"{username_base}{counter}"
                        counter += 1
                    
                    if verbose:
                        self.stdout.write(self.style.SUCCESS(
                            f'CREATE: New user {username} ({email}) for stakeholder {stakeholder.id}'
                        ))
                    
                    if not dry_run:
                        # Create user
                        if stakeholder.stakeholder_type == 'INDIVIDUAL':
                            first_name = stakeholder.first_name or ''
                            last_name = stakeholder.last_name or ''
                        else:
                            first_name = stakeholder.company_name or ''
                            last_name = ''
                        
                        user = User.objects.create_user(
                            username=username,
                            email=email,
                            first_name=first_name[:150],
                            last_name=last_name[:150],
                            password=_generate_random_password(length=16)
                        )
                        user.is_active = True
                        user.save()
                        
                        # Assign to entity
                        UserEntity.objects.get_or_create(
                            user=user,
                            entity=stakeholder.entity,
                            defaults={
                                'is_default': True,
                                'can_switch': False,
                                'assigned_by': None
                            }
                        )
                        
                        # Grant permissions
                        readable_modules = ['shareholder_management', 'accounting']
                        for module in readable_modules:
                            ModulePermission.objects.create(
                                user=user,
                                module=module,
                                can_view=True,
                                can_add=False,
                                can_edit=False,
                                can_delete=False,
                                can_review=False,
                                can_approve=False,
                                can_export=True,
                                access_level='Read Only',
                                is_active=True,
                                granted_by=None
                            )
                    
                    created_count += 1
                    
                except Exception as e:
                    error_count += 1
                    self.stdout.write(self.style.ERROR(
                        f'ERROR: Failed to create user for stakeholder {stakeholder.id} ({email}): {str(e)}'
                    ))
                    if verbose:
                        logger.exception(f"Error creating user for stakeholder {stakeholder.id}")
        
        # Print summary
        self.stdout.write('\n--- Summary ---\n')
        self.stdout.write(f'Total Shareholders:      {all_stakeholders.count()}')
        self.stdout.write(f'Users Created:           {self.style.SUCCESS(str(created_count))}')
        self.stdout.write(f'Users Updated:           {self.style.SUCCESS(str(updated_count))}')
        self.stdout.write(f'Shareholders Skipped:    {self.style.WARNING(str(skipped_count))}')
        self.stdout.write(f'Errors:                  {self.style.ERROR(str(error_count))}')
        
        # Sync status
        synced_count = created_count + updated_count
        self.stdout.write(f'\nTotal Synced:            {self.style.SUCCESS(str(synced_count))}')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('\nDRY RUN - No changes were made'))
            self.stdout.write('Run without --dry-run flag to apply changes')
        else:
            self.stdout.write(self.style.SUCCESS('\n✓ Sync completed successfully!'))
        
        self.stdout.write('')


def _generate_random_password(length=16):
    """Generate a random password"""
    alphabet = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(secrets.choice(alphabet) for _ in range(length))
    return password
