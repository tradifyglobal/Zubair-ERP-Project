

# Theme Management Admin
@admin.register(Theme)
class ThemeAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'name', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'display_name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Theme Information', {
            'fields': ('name', 'display_name', 'description', 'is_active')
        }),
        ('Media', {
            'fields': ('thumbnail_url',),
            'classes': ('collapse',)
        }),
        ('System', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(UserThemePreference)
class UserThemePreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'theme', 'sidebar_color', 'layout_mode')
    list_filter = ('theme', 'layout_mode', 'created_at')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('user', 'created_at', 'updated_at')
    
    fieldsets = (
        ('User & Theme', {
            'fields': ('user', 'theme')
        }),
        ('Layout Preferences', {
            'fields': ('sidebar_color', 'layout_mode', 'layout_size')
        }),
        ('System', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        """Prevent manual creation - preferences are auto-created by signal."""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Prevent deletion - preferences are tied to user."""
        return False
