"""
Django Admin configuration for RBAC models.
Enables web-based role and permission management.
"""

from django.contrib import admin
from django.utils.html import format_html
from .role_models import Role, UserRole, Permission, UserPermissionLog


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    """Admin interface for financial roles."""
    
    list_display = ('name', 'hierarchy_level_display', 'permission_flags', 'is_active', 'created_at')
    list_filter = ('hierarchy_level', 'is_active', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Role Information', {
            'fields': ('name', 'description', 'hierarchy_level', 'is_active')
        }),
        ('Permissions', {
            'fields': (
                'can_create', 'can_read', 'can_update', 'can_delete',
                'can_approve', 'can_post', 'can_export'
            ),
            'description': 'Check the permissions this role should have'
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def hierarchy_level_display(self, obj):
        """Display hierarchy level with color coding."""
        level = obj.hierarchy_level
        colors = {
            0: '#d4edda',  # Green
            1: '#d1ecf1',  # Light blue
            2: '#fff3cd',  # Yellow
            3: '#ffe0b2',  # Orange
            4: '#ffccbc',  # Light orange
            5: '#ffab91',  # Orange red
            6: '#ef9a9a',  # Red
        }
        level_names = {
            0: 'Accountant',
            1: 'Supervisor',
            2: 'Controller',
            3: 'Manager',
            4: 'Director',
            5: 'CFO',
            6: 'Board',
        }
        return format_html(
            '<span style="background-color: {}; padding: 3px 8px; border-radius: 3px;">{}</span>',
            colors.get(level, '#f0f0f0'),
            f'Level {level}: {level_names.get(level, "Unknown")}'
        )
    hierarchy_level_display.short_description = 'Hierarchy Level'

    def permission_flags(self, obj):
        """Display permission flags as badges."""
        perms = []
        if obj.can_create:
            perms.append('<span class="badge badge-success">Create</span>')
        if obj.can_approve:
            perms.append('<span class="badge badge-info">Approve</span>')
        if obj.can_post:
            perms.append('<span class="badge badge-warning">Post</span>')
        if obj.can_export:
            perms.append('<span class="badge badge-secondary">Export</span>')
        return format_html(' '.join(perms))
    permission_flags.short_description = 'Permissions'


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    """Admin interface for user role assignments."""
    
    list_display = ('user_display', 'role_display', 'entity_display', 'is_active', 'granted_at')
    list_filter = ('role', 'is_active', 'granted_at', 'entity')
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name', 'role__name')
    readonly_fields = ('granted_at', 'revoked_at', 'granted_by_display', 'revoked_by_display')

    fieldsets = (
        ('Assignment', {
            'fields': ('user', 'role', 'entity', 'is_active')
        }),
        ('Grant Tracking', {
            'fields': ('granted_by_display', 'granted_at'),
        }),
        ('Revocation Tracking', {
            'fields': ('revoked_by_display', 'revoked_at', 'revocation_reason'),
            'classes': ('collapse',)
        }),
    )

    def user_display(self, obj):
        """Display user with link."""
        return f"{obj.user.get_full_name()} ({obj.user.username})"
    user_display.short_description = 'User'

    def role_display(self, obj):
        """Display role with hierarchy level."""
        return f"{obj.role.name} (L{obj.role.hierarchy_level})"
    role_display.short_description = 'Role'

    def entity_display(self, obj):
        """Display entity name."""
        return obj.entity.name
    entity_display.short_description = 'Entity'

    def granted_by_display(self, obj):
        """Display who granted the role."""
        if obj.granted_by:
            return f"{obj.granted_by.get_full_name()} ({obj.granted_at.strftime('%Y-%m-%d %H:%M')})"
        return '—'
    granted_by_display.short_description = 'Granted By'

    def revoked_by_display(self, obj):
        """Display who revoked the role."""
        if obj.revoked_by:
            return f"{obj.revoked_by.get_full_name()} ({obj.revoked_at.strftime('%Y-%m-%d %H:%M')})"
        return '—'
    revoked_by_display.short_description = 'Revoked By'

    actions = ['revoke_roles']

    def revoke_roles(self, request, queryset):
        """Bulk action to revoke roles."""
        updated = queryset.update(is_active=False, revoked_by=request.user, revoked_at=timezone.now())
        self.message_user(request, f'✓ Revoked {updated} role assignments')
    revoke_roles.short_description = 'Revoke selected role assignments'


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    """Admin interface for granular permissions."""
    
    list_display = ('display_name', 'resource_display', 'action_display', 'role_list', 'conditions_display')
    list_filter = ('resource_type', 'model', 'action', 'role')
    search_fields = ('resource_type', 'model', 'action', 'role__name')
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Permission Identification', {
            'fields': ('resource_type', 'model', 'action')
        }),
        ('Role Assignment', {
            'fields': ('role',),
            'description': 'Which role(s) have this permission'
        }),
        ('Conditions', {
            'fields': (
                'can_view_own_only', 'can_modify_own_only', 'amount_limit',
                'requires_approval', 'min_approval_hierarchy'
            ),
            'description': 'Conditions that must be met for permission grant'
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def display_name(self, obj):
        """Display permission as readable name."""
        return f"{obj.action} {obj.model}"
    display_name.short_description = 'Permission'

    def resource_display(self, obj):
        """Display resource type with color."""
        colors = {
            'accounting': '#e3f2fd',
            'shareholder': '#e8f5e9',
            'reporting': '#fff3e0',
            'compliance': '#fce4ec',
            'system': '#f3e5f5',
        }
        return format_html(
            '<span style="background-color: {}; padding: 2px 6px; border-radius: 3px;">{}</span>',
            colors.get(obj.resource_type, '#f0f0f0'),
            obj.resource_type
        )
    resource_display.short_description = 'Resource'

    def action_display(self, obj):
        """Display action with icon."""
        icons = {
            'CREATE': '➕',
            'READ': '👁️',
            'UPDATE': '✏️',
            'DELETE': '🗑️',
            'APPROVE': '✅',
            'REJECT': '❌',
            'POST': '📤',
            'RECONCILE': '⚖️',
            'CLOSE_PERIOD': '🔒',
            'EXPORT': '📥',
        }
        return f"{icons.get(obj.action, '')} {obj.action}"
    action_display.short_description = 'Action'

    def role_list(self, obj):
        """Display roles that have this permission."""
        roles = obj.role.values_list('name', flat=True)
        return ', '.join(roles) if roles else '—'
    role_list.short_description = 'Roles'

    def conditions_display(self, obj):
        """Display conditions as badges."""
        conditions = []
        if obj.can_view_own_only:
            conditions.append('👁️ View Own Only')
        if obj.can_modify_own_only:
            conditions.append('✏️ Modify Own Only')
        if obj.amount_limit:
            conditions.append(f'💰 ≤ {obj.amount_limit:,.0f}')
        if obj.requires_approval:
            conditions.append('✅ Needs Approval')
        return ' | '.join(conditions) if conditions else '—'
    conditions_display.short_description = 'Conditions'


@admin.register(UserPermissionLog)
class UserPermissionLogAdmin(admin.ModelAdmin):
    """Admin interface for permission audit trail (read-only)."""
    
    list_display = ('user_display', 'result_display', 'action_display', 'timestamp')
    list_filter = ('result', 'action', 'timestamp', 'resource_type')
    search_fields = ('user__username', 'entity__name', 'ip_address')
    readonly_fields = ('user', 'entity', 'resource_type', 'model', 'action', 'result', 'reason', 'ip_address', 'user_agent', 'timestamp')

    def has_add_permission(self, request):
        """Disable adding records (auto-created by system)."""
        return False

    def has_delete_permission(self, request, obj=None):
        """Disable deleting audit logs."""
        return False

    def has_change_permission(self, request, obj=None):
        """Disable editing audit logs."""
        return False

    fieldsets = (
        ('User & Context', {
            'fields': ('user', 'entity', 'ip_address', 'user_agent')
        }),
        ('Permission Details', {
            'fields': ('resource_type', 'model', 'action')
        }),
        ('Result', {
            'fields': ('result', 'reason')
        }),
        ('Timestamp', {
            'fields': ('timestamp',)
        }),
    )

    def user_display(self, obj):
        """Display user."""
        return f"{obj.user.get_full_name()} ({obj.user.username})"
    user_display.short_description = 'User'

    def result_display(self, obj):
        """Display result with color."""
        colors = {
            'GRANTED': '#c8e6c9',  # Green
            'DENIED': '#ffcccc',   # Red
            'AUDIT': '#fff9c4',    # Yellow
        }
        return format_html(
            '<span style="background-color: {}; padding: 3px 8px; border-radius: 3px;">{}</span>',
            colors.get(obj.result, '#f0f0f0'),
            obj.result
        )
    result_display.short_description = 'Result'

    def action_display(self, obj):
        """Display action."""
        return obj.action if obj.action else '—'
    action_display.short_description = 'Action'


from django.utils import timezone
