from django.contrib import admin
from django.utils.html import format_html
from .models import AuditLog, SecurityEvent, DataAccessLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('action', 'model_name', 'user', 'timestamp', 'success_badge', 'ip_address')
    list_filter = ('action', 'success', 'timestamp', 'model_name')
    search_fields = ('user__username', 'ip_address', 'model_name')
    readonly_fields = ('timestamp', 'old_values', 'new_values', 'changed_fields')
    date_hierarchy = 'timestamp'
    
    def success_badge(self, obj):
        if obj.success:
            color = 'green'
            text = 'Success'
        else:
            color = 'red'
            text = 'Failed'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, text
        )
    success_badge.short_description = 'Status'
    
    def has_add_permission(self, request):
        return False  # Don't allow manual creation


@admin.register(SecurityEvent)
class SecurityEventAdmin(admin.ModelAdmin):
    list_display = ('event_type', 'severity_badge', 'ip_address', 'user', 'timestamp', 'resolved_badge')
    list_filter = ('event_type', 'severity', 'resolved', 'timestamp')
    search_fields = ('description', 'ip_address', 'user__username')
    readonly_fields = ('timestamp', 'description', 'event_type', 'ip_address')
    date_hierarchy = 'timestamp'
    
    fieldsets = (
        ('Event Details', {
            'fields': ('event_type', 'description', 'severity')
        }),
        ('Source Information', {
            'fields': ('ip_address', 'user')
        }),
        ('Resolution', {
            'fields': ('resolved', 'resolution_notes')
        }),
        ('Timestamp', {
            'fields': ('timestamp',),
            'classes': ('collapse',)
        }),
    )
    
    def severity_badge(self, obj):
        colors = {1: 'green', 2: 'orange', 3: 'red', 4: 'darkred'}
        color = colors.get(obj.severity, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_severity_display()
        )
    severity_badge.short_description = 'Severity'
    
    def resolved_badge(self, obj):
        color = 'green' if obj.resolved else 'red'
        text = 'Resolved' if obj.resolved else 'Unresolved'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, text
        )
    resolved_badge.short_description = 'Status'


@admin.register(DataAccessLog)
class DataAccessLogAdmin(admin.ModelAdmin):
    list_display = ('data_type', 'object_id', 'user', 'action', 'timestamp', 'ip_address')
    list_filter = ('data_type', 'action', 'timestamp')
    search_fields = ('user__username', 'data_type', 'ip_address')
    readonly_fields = ('timestamp',)
    date_hierarchy = 'timestamp'
    
    def has_add_permission(self, request):
        return False  # Don't allow manual creation
