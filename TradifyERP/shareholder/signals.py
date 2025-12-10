"""
Signals for Shareholder Module
Handles automatic user creation when stakeholders are created
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from accounting.models import Stakeholder, UserEntity
import logging
import secrets
import string

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Stakeholder)
def create_user_for_stakeholder(sender, instance, created, **kwargs):
    """
    Automatically create a Django user when a new stakeholder is created.
    Also assign the user to the stakeholder's entity.
    """
    if not created:
        # Only process new stakeholder creations, not updates
        return
    
    try:
        # Generate username from email (remove domain part or use email prefix)
        email = instance.email
        username_base = email.split('@')[0] if email else None
        
        if not username_base:
            logger.warning(f"Cannot create user for stakeholder {instance.id}: no email provided")
            return
        
        # Make username unique by checking if it exists
        username = username_base
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{username_base}{counter}"
            counter += 1
        
        # Determine first and last name
        if instance.stakeholder_type == 'INDIVIDUAL':
            first_name = instance.first_name or ''
            last_name = instance.last_name or ''
        else:  # CORPORATE or other types
            first_name = instance.company_name or ''
            last_name = ''
        
        # Create the Django user
        user = User.objects.create_user(
            username=username,
            email=instance.email,
            first_name=first_name[:150],  # Django max length is 150
            last_name=last_name[:150],
            password=_generate_random_password(length=16)
        )
        
        # Mark as active
        user.is_active = True
        user.save()
        
        # Assign user to the stakeholder's entity
        UserEntity.objects.get_or_create(
            user=user,
            entity=instance.entity,
            defaults={
                'is_default': True,
                'can_switch': False,  # Shareholders can only access their own entity
                'assigned_by': None  # Automatically assigned by system
            }
        )
        
        # Grant module permissions to shareholders (read-only for most modules)
        from accounting.module_permissions import ModulePermission
        
        # Grant read-only access to relevant modules
        readable_modules = [
            'shareholder_management',
            'accounting',
        ]
        
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
                can_export=True,  # Allow export for their own data
                access_level='Read Only',
                is_active=True,
                granted_by=None  # System-granted
            )
        
        logger.info(
            f"Successfully created user '{username}' for stakeholder "
            f"{instance.id} ({instance.email}) in entity {instance.entity.code}"
        )
        
    except Exception as e:
        logger.error(
            f"Error creating user for stakeholder {instance.id} ({instance.email}): {str(e)}",
            exc_info=True
        )


@receiver(post_save, sender=Stakeholder)
def update_user_for_stakeholder(sender, instance, created, **kwargs):
    """
    Update user information when stakeholder information is updated.
    """
    if created:
        # Skip if this is a new creation (handled by create_user_for_stakeholder)
        return
    
    try:
        # Find user by email
        try:
            user = User.objects.get(email=instance.email)
        except User.DoesNotExist:
            # User doesn't exist, skip update
            return
        
        # Update user information
        if instance.stakeholder_type == 'INDIVIDUAL':
            user.first_name = (instance.first_name or '')[:150]
            user.last_name = (instance.last_name or '')[:150]
        else:  # CORPORATE
            user.first_name = (instance.company_name or '')[:150]
            user.last_name = ''
        
        # Update email if changed
        if user.email != instance.email:
            user.email = instance.email
        
        user.save()
        
        logger.info(f"Updated user information for stakeholder {instance.id} ({instance.email})")
        
    except Exception as e:
        logger.error(
            f"Error updating user for stakeholder {instance.id} ({instance.email}): {str(e)}",
            exc_info=True
        )


def _generate_random_password(length=16):
    """Generate a random password"""
    alphabet = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(secrets.choice(alphabet) for _ in range(length))
    return password
