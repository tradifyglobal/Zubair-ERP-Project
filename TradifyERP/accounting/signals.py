"""
Accounting Module Signals
Auto-create UserRole entries for new users.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

from .models import Entity
from .role_models import UserRole, Role


@receiver(post_save, sender=User)
def create_user_role_for_new_user(sender, instance, created, **kwargs):
    """
    Automatically assign new users to the default entity with Admin role.
    This ensures new users can see entities and employees immediately upon login.
    """
    if not created:
        return  # Only process new users
    
    # Don't create roles for superusers or staff automatically
    # They should be assigned manually
    if instance.is_superuser or instance.is_staff:
        return
    
    try:
        # Get or create the default entity (usually the first one)
        entity = Entity.objects.first()
        if not entity:
            return  # No entity exists yet
        
        # Get or create Admin role
        admin_role, _ = Role.objects.get_or_create(
            name='Admin',
            defaults={'description': 'Administrator role'}
        )
        
        # Check if user already has a role for this entity
        existing_role = UserRole.objects.filter(
            user=instance,
            entity=entity
        ).exists()
        
        if not existing_role:
            # Create UserRole for the new user
            UserRole.objects.create(
                user=instance,
                entity=entity,
                role=admin_role,
                is_active=True
            )
    except Exception as e:
        # Silently fail - don't break user creation if role assignment fails
        pass
