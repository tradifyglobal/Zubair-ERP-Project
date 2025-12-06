# TooManyFieldsSent Error Fix

## Problem
When editing a Django User in the admin panel, the following error occurred:
```
TooManyFieldsSent at /admin/auth/user/15/change/
The number of GET/POST parameters exceeded settings.DATA_UPLOAD_MAX_NUMBER_FIELDS.
```

## Root Cause
The `CustomUserAdmin` class included `ModulePermissionInline` which created inline form rows for each module permission a user has. When a user has many permissions or there are many modules, the total number of form fields can exceed Django's default limit of **1000 fields**.

### Field Count Calculation
- Base User form: ~12 fields
- Each ModulePermissionInline row: ~9 fields (module, can_view, can_add, can_edit, can_delete, can_review, can_approve, can_export, is_active)
- With 100+ module permissions: 12 + (100 × 9) = **912 fields** ✓ OK
- With 150+ module permissions: 12 + (150 × 9) = **1,362 fields** ✗ EXCEEDS LIMIT (1000)

## Solution Implemented

### 1. Removed ModulePermissionInline from CustomUserAdmin
**File:** `accounting/admin.py`

Changed from:
```python
@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    """Extended User admin with module permissions."""
    inlines = BaseUserAdmin.inlines + (ModulePermissionInline,)
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Module Permissions', {
            'fields': (),
            'description': 'Manage module permissions using the "Module Permissions" section below'
        }),
    )
```

To:
```python
@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    """Extended User admin for basic user management."""
    # Module permissions are managed via the dedicated ModulePermissionAdmin
    pass
```

**Rationale:**
- Eliminates inline form field explosion
- Provides cleaner UX (edit user, then edit permissions separately)
- Improves performance (fewer fields to render)
- Follows Django best practices for large datasets

### 2. Increased Django Settings (Fallback)
**File:** `TradifyERP/settings.py`

Added as failsafe:
```python
# Data Upload Settings
DATA_UPLOAD_MAX_NUMBER_FIELDS = 10000
DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB
```

This provides a buffer for other admin forms that might need more fields.

## User Workflow Change

### Before (Broken)
1. Go to `/admin/auth/user/15/change/`
2. ❌ TooManyFieldsSent error
3. Cannot edit user

### After (Fixed)
1. **Edit User:** Go to `/admin/auth/user/15/change/`
   - Change basic info, password, groups, etc.
   - Save successfully

2. **Edit Permissions:** Go to `/admin/accounting/modulepermission/`
   - Filter by user
   - Add/edit/delete permissions
   - Manages all permission-related fields

## Result

✅ **Fixed Issues:**
- Users with many module permissions can be edited successfully
- Form never exceeds field limit
- Clean separation of concerns (user vs permissions)
- Better performance (fewer inline records)

## Testing

To verify the fix works:

1. **Restart Django server** to load new settings
2. **Open admin panel:** `/admin/auth/user/`
3. **Edit any user:** Click on a user to open change form
4. **Check form loads:** Should load without "TooManyFieldsSent" error
5. **View permissions:** ModulePermissionInline should display (max 100 rows)

## Future Considerations

### Option 1: Move Permissions to Separate Admin Link
Instead of inline, show link to dedicated permission admin page:
```python
@admin.register(ModulePermission)
class ModulePermissionAdmin(admin.ModelAdmin):
    list_display = ('user', 'module', 'can_view', 'can_add', 'can_edit', 'is_active')
    list_filter = ('module', 'is_active')
    search_fields = ('user__username', 'module__name')
    
    def get_queryset(self, request):
        # Filter to current user's permissions by default
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            return qs.filter(user=request.user)
        return qs
```

Then remove inline from CustomUserAdmin:
```python
@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    # Don't include ModulePermissionInline, link to separate admin instead
    list_display = BaseUserAdmin.list_display + ('get_permissions_url',)
    
    def get_permissions_url(self, obj):
        url = f'/admin/accounting/modulepermission/?user_id={obj.id}'
        return f'<a href="{url}">View Permissions</a>'
    get_permissions_url.short_description = 'Permissions'
    get_permissions_url.allow_tags = True
```

### Option 2: Use Raw ID Field
Replace inline with raw_id field for large datasets:
```python
class CustomUserAdmin(BaseUserAdmin):
    raw_id_fields = ('user',) + BaseUserAdmin.raw_id_fields
```

## Files Modified
- `TradifyERP/settings.py` - Added DATA_UPLOAD settings
- `accounting/admin.py` - Optimized ModulePermissionInline

## References
- [Django DATA_UPLOAD_MAX_NUMBER_FIELDS](https://docs.djangoproject.com/en/5.2/ref/settings/#data-upload-max-number-fields)
- [Django DATA_UPLOAD_MAX_MEMORY_SIZE](https://docs.djangoproject.com/en/5.2/ref/settings/#data-upload-max-memory-size)
- [Django Admin Inline Fields](https://docs.djangoproject.com/en/5.2/ref/contrib/admin/#working-with-many-to-many-models)
