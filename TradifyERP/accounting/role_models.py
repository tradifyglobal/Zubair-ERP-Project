"""
Role-Based Access Control (RBAC) models for financial system compliance.
Implements SOX 404 segregation of duties and COSO framework requirements.
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Entity


class Role(models.Model):
    """
    Financial roles for segregation of duties.
    Based on COSO Internal Control Framework.
    """
    ROLE_CHOICES = [
        ('ACCOUNTANT', 'Accountant'),
        ('REVIEWER', 'Reviewer / Supervisor'),
        ('MANAGER', 'Finance Manager'),
        ('AUDITOR', 'Internal Auditor'),
        ('CFO', 'Chief Financial Officer'),
        ('BOARD', 'Board Member'),
        ('ADMIN', 'System Administrator'),
    ]

    name = models.CharField(
        max_length=50,
        choices=ROLE_CHOICES,
        unique=True
    )
    description = models.TextField(
        help_text="Role responsibilities and segregation of duties"
    )
    
    # Hierarchy level for approval chains
    hierarchy_level = models.IntegerField(
        default=0,
        help_text="0=lowest (Accountant), 6=highest (Board). Used for approval routing."
    )

    # Permissions summary
    can_create_entries = models.BooleanField(default=False)
    can_approve_entries = models.BooleanField(default=False)
    can_post_entries = models.BooleanField(default=False)
    can_modify_entries = models.BooleanField(default=False)
    can_delete_entries = models.BooleanField(default=False)
    can_view_audit_trail = models.BooleanField(default=False)
    can_close_periods = models.BooleanField(default=False)
    can_reconcile = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['hierarchy_level']

    def __str__(self):
        return f"{self.get_name_display()} (Level {self.hierarchy_level})"


class UserRole(models.Model):
    """
    User to role assignment with entity-level granularity.
    Allows different roles per entity (multi-tenant).
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='financial_roles'
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name='user_assignments'
    )
    entity = models.ForeignKey(
        Entity,
        on_delete=models.CASCADE,
        related_name='user_roles'
    )

    # Audit trail
    granted_date = models.DateTimeField(default=timezone.now)
    granted_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='granted_roles'
    )
    revoked_date = models.DateTimeField(null=True, blank=True)
    revoked_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='revoked_roles'
    )
    revocation_reason = models.TextField(blank=True, null=True)

    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('user', 'role', 'entity')
        ordering = ['user__username', 'role__hierarchy_level']

    def __str__(self):
        return f"{self.user.username} - {self.role.name} ({self.entity.code})"

    def revoke(self, revoked_by, reason=""):
        """Revoke this role assignment."""
        self.is_active = False
        self.revoked_date = timezone.now()
        self.revoked_by = revoked_by
        self.revocation_reason = reason
        self.save()


class Permission(models.Model):
    """
    Granular permission definition.
    Defines what actions each role can perform on which models.
    """
    RESOURCE_TYPES = [
        ('accounting', 'Accounting'),
        ('shareholder', 'Shareholder'),
        ('reporting', 'Reporting'),
        ('compliance', 'Compliance'),
        ('system', 'System Administration'),
    ]

    MODEL_CHOICES = [
        ('LedgerEntry', 'Ledger Entry'),
        ('Account', 'Chart of Accounts'),
        ('TrialBalance', 'Trial Balance'),
        ('CapitalContribution', 'Capital Contribution'),
        ('Stakeholder', 'Stakeholder'),
        ('Shareholding', 'Shareholding'),
        ('PeriodLock', 'Period Lock'),
        ('ReconciliationRecord', 'Reconciliation'),
        ('FinancialStatement', 'Financial Statement'),
        ('AuditLog', 'Audit Log'),
    ]

    ACTION_CHOICES = [
        ('CREATE', 'Create'),
        ('READ', 'Read'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
        ('APPROVE', 'Approve'),
        ('REJECT', 'Reject'),
        ('POST', 'Post to GL'),
        ('RECONCILE', 'Reconcile'),
        ('CLOSE_PERIOD', 'Close Period'),
        ('EXPORT', 'Export'),
    ]

    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name='permissions'
    )
    
    resource = models.CharField(max_length=50, choices=RESOURCE_TYPES)
    model = models.CharField(max_length=100, choices=MODEL_CHOICES)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)

    # Conditions
    can_view_own_only = models.BooleanField(
        default=False,
        help_text="Can only view records created by this user"
    )
    can_modify_own_only = models.BooleanField(
        default=False,
        help_text="Can only modify records created by this user"
    )
    amount_limit = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Maximum transaction amount (if applicable)"
    )

    # Approval requirement
    requires_approval = models.BooleanField(
        default=False,
        help_text="Actions by this role require approval"
    )
    min_approval_hierarchy = models.IntegerField(
        default=0,
        help_text="Minimum role hierarchy level required for approval"
    )

    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('role', 'resource', 'model', 'action')
        ordering = ['role__hierarchy_level', 'resource', 'model', 'action']

    def __str__(self):
        return f"{self.role.name}: {self.action} {self.model}"


class UserPermissionLog(models.Model):
    """
    Audit log for permission checks.
    Tracks every permission evaluation (failed and successful).
    """
    REQUEST_RESULT = [
        ('GRANTED', 'Permission Granted'),
        ('DENIED', 'Permission Denied'),
        ('AUDIT', 'Audit Access Granted'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='permission_logs'
    )
    entity = models.ForeignKey(
        Entity,
        on_delete=models.CASCADE,
        related_name='permission_logs'
    )

    resource = models.CharField(max_length=50)
    model = models.CharField(max_length=100)
    action = models.CharField(max_length=20)
    object_id = models.CharField(max_length=100, blank=True)

    result = models.CharField(max_length=20, choices=REQUEST_RESULT)
    reason = models.TextField(blank=True)

    request_ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['entity', '-timestamp']),
            models.Index(fields=['result', '-timestamp']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.result} - {self.action} {self.model}"
