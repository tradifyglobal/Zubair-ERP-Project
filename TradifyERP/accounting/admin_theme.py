"""
Django Admin configuration for theme management.
Allows administrators to:
- Add/edit/delete available themes
- Manage which themes are active
- View user theme preferences
"""

from django.contrib import admin
from accounting.models_theme import Theme, UserThemePreference


@admin.register(Theme)
class ThemeAdmin(admin.ModelAdmin):
    list_display = ['name', 'display_name', 'is_active', 'created_at', 'updated_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'display_name', 'description']
    ordering = ['name']
    
    fieldsets = (
        ('Theme Identification', {
            'fields': ('name', 'display_name', 'description'),
        }),
        ('Theme Configuration', {
            'fields': ('is_active', 'thumbnail_url'),
            'description': 'Configure theme availability and appearance',
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')


@admin.register(UserThemePreference)
class UserThemePreferenceAdmin(admin.ModelAdmin):
    list_display = ['user', 'theme', 'sidebar_color', 'layout_mode', 'layout_size', 'updated_at']
    list_filter = ['theme', 'sidebar_color', 'layout_mode', 'layout_size', 'updated_at']
    search_fields = ['user__username', 'user__email']
    ordering = ['user__username']
    
    fieldsets = (
        ('User & Theme', {
            'fields': ('user', 'theme'),
        }),
        ('Layout Preferences', {
            'fields': ('sidebar_color', 'layout_mode', 'layout_size'),
            'description': 'User-specific layout and appearance settings',
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def has_add_permission(self, request):
        """Prevent manual creation - preferences are auto-created with users"""
        return False
