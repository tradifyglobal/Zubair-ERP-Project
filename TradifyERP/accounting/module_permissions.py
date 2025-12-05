"""
Module-based Access Control for TradifyERP.
Allows administrators to control which modules each user can access 
and what actions they can perform (View, Add, Edit, Delete).
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class ModulePermission(models.Model):
    """
    Defines which modules a user can access and their permission levels.
    """
    
    MODULE_CHOICES = [
        ('accounting', 'Accounting & Finance'),
        ('hr', 'Human Resources'),
        ('manufacturing', 'Manufacturing'),
        ('sales', 'Sales Management'),
        ('inventory', 'Inventory Management'),
        ('procurement', 'Procurement'),
        ('ap', 'Accounts Payable'),
        ('ar', 'Accounts Receivable'),
        ('crm', 'Customer Relationship Management'),
        ('projects', 'Project Management'),
        ('cash_management', 'Cash Management'),
        ('shareholder', 'Shareholder Management'),
        ('maintenance', 'Site Maintenance'),
        ('reviewer', 'Workflow Reviewer'),
        ('approver', 'Workflow Approver'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='module_permissions'
    )
    
    module = models.CharField(
        max_length=50,
        choices=MODULE_CHOICES,
        help_text="The module this permission applies to"
    )
    
    # Granular permissions
    can_view = models.BooleanField(
        default=False,
        help_text="Can view/read records in this module"
    )
    
    can_add = models.BooleanField(
        default=False,
        help_text="Can create new records in this module"
    )
    
    can_edit = models.BooleanField(
        default=False,
        help_text="Can modify existing records in this module"
    )
    
    can_delete = models.BooleanField(
        default=False,
        help_text="Can delete records in this module"
    )
    
    # Additional controls
    can_review = models.BooleanField(
        default=False,
        help_text="Can review transactions in this module"
    )
    
    can_approve = models.BooleanField(
        default=False,
        help_text="Can approve transactions in this module"
    )
    
    can_export = models.BooleanField(
        default=False,
        help_text="Can export data from this module"
    )
    
    # Access level description
    access_level = models.CharField(
        max_length=50,
        blank=True,
        help_text="Description: Full Access, Read Only, Limited, etc."
    )
    
    # Audit fields
    granted_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='granted_module_permissions'
    )
    
    granted_date = models.DateTimeField(default=timezone.now)
    
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this permission is currently active"
    )
    
    notes = models.TextField(
        blank=True,
        help_text="Additional notes about this permission"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user', 'module')
        ordering = ['user__username', 'module']
        verbose_name = "Module Permission"
        verbose_name_plural = "Module Permissions"
        indexes = [
            models.Index(fields=['user', 'module']),
            models.Index(fields=['module', 'is_active']),
        ]
    
    def __str__(self):
        permissions = []
        if self.can_view:
            permissions.append('View')
        if self.can_add:
            permissions.append('Add')
        if self.can_edit:
            permissions.append('Edit')
        if self.can_delete:
            permissions.append('Delete')
        
        perm_str = ', '.join(permissions) if permissions else 'No Access'
        return f"{self.user.username} - {self.get_module_display()}: {perm_str}"
    
    @property
    def permission_summary(self):
        """Returns a readable summary of permissions."""
        perms = []
        if self.can_view:
            perms.append('View')
        if self.can_add:
            perms.append('Add')
        if self.can_edit:
            perms.append('Edit')
        if self.can_delete:
            perms.append('Delete')
        if self.can_review:
            perms.append('Review')
        if self.can_approve:
            perms.append('Approve')
        if self.can_export:
            perms.append('Export')
        
        return ', '.join(perms) if perms else 'No Access'
    
    @property
    def has_full_access(self):
        """Check if user has full access (all permissions)."""
        return all([
            self.can_view,
            self.can_add,
            self.can_edit,
            self.can_delete
        ])
    
    @property
    def is_read_only(self):
        """Check if user has read-only access."""
        return self.can_view and not any([
            self.can_add,
            self.can_edit,
            self.can_delete
        ])
    
    @classmethod
    def user_can_access_module(cls, user, module_name):
        """Check if user has any access to a module."""
        if user.is_superuser:
            return True
        
        permission = cls.objects.filter(
            user=user,
            module=module_name,
            is_active=True
        ).first()
        
        return permission is not None and permission.can_view
    
    @classmethod
    def user_can_perform_action(cls, user, module_name, action):
        """
        Check if user can perform a specific action on a module.
        action can be: 'view', 'add', 'edit', 'delete', 'approve', 'export'
        """
        if user.is_superuser:
            return True
        
        permission = cls.objects.filter(
            user=user,
            module=module_name,
            is_active=True
        ).first()
        
        if not permission:
            return False
        
        action_map = {
            'view': permission.can_view,
            'add': permission.can_add,
            'edit': permission.can_edit,
            'delete': permission.can_delete,
            'approve': permission.can_approve,
            'export': permission.can_export,
        }
        
        return action_map.get(action.lower(), False)
    
    @classmethod
    def get_user_modules(cls, user):
        """Get all modules the user has access to."""
        if user.is_superuser:
            return [choice[0] for choice in cls.MODULE_CHOICES]
        
        return list(cls.objects.filter(
            user=user,
            is_active=True,
            can_view=True
        ).values_list('module', flat=True))
    
    @classmethod
    def grant_full_access(cls, user, module, granted_by=None):
        """Grant full access to a module for a user."""
        permission, created = cls.objects.get_or_create(
            user=user,
            module=module,
            defaults={
                'can_view': True,
                'can_add': True,
                'can_edit': True,
                'can_delete': True,
                'can_approve': True,
                'can_export': True,
                'access_level': 'Full Access',
                'granted_by': granted_by,
                'is_active': True,
            }
        )
        
        if not created:
            permission.can_view = True
            permission.can_add = True
            permission.can_edit = True
            permission.can_delete = True
            permission.can_approve = True
            permission.can_export = True
            permission.access_level = 'Full Access'
            permission.granted_by = granted_by
            permission.is_active = True
            permission.save()
        
        return permission
    
    @classmethod
    def grant_read_only_access(cls, user, module, granted_by=None):
        """Grant read-only access to a module for a user."""
        permission, created = cls.objects.get_or_create(
            user=user,
            module=module,
            defaults={
                'can_view': True,
                'can_add': False,
                'can_edit': False,
                'can_delete': False,
                'can_approve': False,
                'can_export': True,
                'access_level': 'Read Only',
                'granted_by': granted_by,
                'is_active': True,
            }
        )
        
        if not created:
            permission.can_view = True
            permission.can_add = False
            permission.can_edit = False
            permission.can_delete = False
            permission.can_approve = False
            permission.can_export = True
            permission.access_level = 'Read Only'
            permission.granted_by = granted_by
            permission.is_active = True
            permission.save()
        
        return permission


class UserModuleAccessLog(models.Model):
    """
    Audit log for module access attempts.
    Tracks when users access different modules and actions.
    """
    
    ACCESS_RESULT = [
        ('ALLOWED', 'Access Allowed'),
        ('DENIED', 'Access Denied'),
        ('WARNING', 'Access with Warning'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='module_access_logs'
    )
    
    module = models.CharField(max_length=50)
    
    action_attempted = models.CharField(
        max_length=50,
        help_text="The action user tried to perform"
    )
    
    result = models.CharField(
        max_length=20,
        choices=ACCESS_RESULT
    )
    
    reason = models.TextField(
        blank=True,
        help_text="Reason for denial or additional context"
    )
    
    request_path = models.CharField(max_length=500, blank=True)
    request_ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Module Access Log"
        verbose_name_plural = "Module Access Logs"
        indexes = [
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['module', '-timestamp']),
            models.Index(fields=['result', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.module} - {self.result} ({self.timestamp})"
