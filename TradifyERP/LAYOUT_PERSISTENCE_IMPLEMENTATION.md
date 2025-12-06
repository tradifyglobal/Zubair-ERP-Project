# Layout Persistence Implementation Complete

## Overview
Successfully implemented persistent layout preference storage so that user layout choices (vertical/horizontal) are saved to the database and automatically restored on page load and navigation.

## Problem Statement
- Users selecting "vertical" layout would see it switch back to "horizontal" after refreshing the page or navigating to other sections
- Layout preference was only stored in localStorage, not in the database
- UserThemePreference model had `layout_mode` field but it wasn't being utilized

## Solution Architecture

### 1. Backend Implementation

#### View Function: `save_layout_preference()` 
**File:** `accounting/views.py` (lines 2595-2630)
```python
@require_http_methods(["POST"])
def save_layout_preference(request):
    """AJAX endpoint to save layout preference to database."""
    try:
        layout = request.POST.get('layout', 'vertical')
        
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'error': 'Not authenticated'}, status=401)
        
        # Get or create user theme preference
        theme_pref, created = UserThemePreference.objects.get_or_create(user=request.user)
        
        # Save layout mode
        theme_pref.layout_mode = 'horizontal' if layout == 'horizontal' else 'vertical'
        theme_pref.save()
        
        return JsonResponse({
            'success': True,
            'layout': layout,
            'message': f'Layout preference saved: {layout}'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)
```

**Features:**
- Validates user authentication before saving
- Uses get_or_create to handle new users automatically
- Proper CSRF protection (no @csrf_exempt)
- JSON response for AJAX handling
- Error handling with appropriate HTTP status codes

#### URL Configuration
**File:** `accounting/urls.py`

**Import added:**
```python
from .views import (
    # ... existing imports ...
    save_layout_preference,
)
```

**URL path added:**
```python
path('api/save-layout-preference/', save_layout_preference, name='save_layout_preference'),
```

### 2. Frontend Implementation

#### Page Load: Server-side Layout Restoration
**File:** `templates/partials/base.html` (line 51)

The `<body>` tag includes:
```html
data-layout="{% if user_theme_pref.layout_mode %}{{ user_theme_pref.layout_mode }}{% else %}vertical{% endif %}"
```

This ensures:
- On page load/refresh, the layout is restored from `UserThemePreference.layout_mode`
- New users default to 'vertical' layout
- No JavaScript logic needed for initial load

#### Layout Change Handler: AJAX Save
**File:** `templates/partials/base.html` (lines 1348-1383)

```javascript
$("input[name='layout']").off('change').on('change', function() {
    var layout = $(this).val();
    
    console.log('[LayoutFix] Layout changed to:', layout);
    
    // Save to localStorage for immediate fallback
    localStorage.setItem('minia-layout', layout);
    
    // Apply layout visually
    applyLayoutView(layout);
    
    // Save to database via AJAX with CSRF token
    var csrftoken = $("[name=csrfmiddlewaretoken]").val();
    $.ajax({
        url: '/accounting/api/save-layout-preference/',
        type: 'POST',
        data: {
            layout: layout,
            csrfmiddlewaretoken: csrftoken
        },
        success: function(response) {
            console.log('[LayoutFix] Layout preference saved to server:', response);
        },
        error: function(xhr, status, error) {
            console.error('[LayoutFix] Error saving layout preference:', error);
        }
    });
    
    // Toggle sidebar settings visibility
    if(layout === 'horizontal') {
        $(".sidebar-setting").hide();
    } else {
        $(".sidebar-setting").show();
    }
    
    return false;
});
```

**Features:**
- Immediate visual change via `applyLayoutView()`
- Background AJAX save to database
- Proper CSRF token inclusion
- Console logging for debugging
- Graceful error handling
- localStorage fallback for offline scenarios

#### CSRF Token Addition
**File:** `templates/partials/base.html` (line 8)

Added `{% csrf_token %}` in the `<head>` section to ensure CSRF token is available to JavaScript.

### 3. Data Flow

```
User changes layout via Theme Customizer
         ↓
JavaScript 'change' event triggered
         ↓
├─→ Visual: applyLayoutView() immediately changes DOM
├─→ Local: localStorage.setItem() for fallback
└─→ Remote: AJAX POST to /accounting/api/save-layout-preference/
                          ↓
                    Backend validates user
                          ↓
                    UserThemePreference.objects.get_or_create()
                          ↓
                    Save layout_mode field
                          ↓
                    JSON response success
         ↓
User navigates or refreshes page
         ↓
Server renders with data-layout="{{ user_theme_pref.layout_mode }}"
         ↓
Layout loads from database (persists)
```

## Configuration Files Modified

| File | Changes | Purpose |
|------|---------|---------|
| `accounting/views.py` | Added `save_layout_preference()` view | Backend endpoint for AJAX calls |
| `accounting/urls.py` | Added import + URL path | Route AJAX requests to view |
| `templates/partials/base.html` | Added CSRF token, AJAX handler, layout restoration logic | Frontend persistence |

## Testing Checklist

✅ **User Authentication**
- AJAX endpoint returns 401 for unauthenticated users
- Authenticated users can save preferences

✅ **Layout Change Flow**
- Clicking layout radio button immediately changes layout
- Console shows "[LayoutFix] Layout changed to: [layout]" 
- Browser shows AJAX POST request in Network tab
- Response shows `"success": True`

✅ **Persistence Across Navigation**
- Change layout to vertical → Save preference
- Navigate to different page (e.g., GL Dashboard) → Layout remains vertical
- No page refresh required

✅ **Persistence Across Refresh**
- Change layout to horizontal → Save preference
- Browser refresh (F5) → Layout loads as horizontal from database
- Layout remains horizontal on all subsequent pages

✅ **Multiple Users**
- User A sets vertical → Logs out
- User B logs in → Sees their own saved layout preference
- User A logs in → Sees vertical layout (their preference)

✅ **Error Handling**
- Network error during AJAX call → Console logs error but doesn't break layout
- Database error → Backend returns 400 status with error message
- CSRF validation → Passes with token from {% csrf_token %}

✅ **New Users**
- New user first login → Defaults to 'vertical' layout
- First layout change → Creates UserThemePreference and saves

## Database Impact

**Table Modified:** `accounting_userth emepreference`
**Field Used:** `layout_mode` (CharField with choices: 'vertical', 'horizontal')
**Migration Status:** No new migration needed - field already exists in model

**Example Data:**
```sql
SELECT user_id, layout_mode FROM accounting_userthemepreference 
WHERE user_id = 5;
-- Result: (5, 'vertical')
```

## Production Considerations

1. **CSRF Protection**: Removed `@csrf_exempt` and now properly validates CSRF tokens
2. **Rate Limiting**: Consider adding rate limiting if this endpoint receives excessive requests
3. **Logging**: View includes exception handling; consider adding audit logging for compliance
4. **Performance**: Single AJAX call per layout change (minimal impact)

## Browser Compatibility

- **Modern Browsers**: ✅ Fully supported (jQuery, AJAX, localStorage)
- **IE 11**: ⚠️ May have issues with modern JavaScript
- **Mobile**: ✅ Fully supported (responsive layout system already in place)

## Debugging Tips

### View Console Logs
Open Browser Developer Tools → Console tab
- Look for `[LayoutFix]` prefixed messages
- Shows layout change tracking and server responses

### Check AJAX Request
Network tab → Filter for `save-layout-preference`
- Verify POST request is sent
- Check request headers (CSRF token included)
- Verify 200 OK response with JSON payload

### Database Query
```python
from accounting.models_theme import UserThemePreference
from django.contrib.auth.models import User

user = User.objects.get(username='testuser')
pref = UserThemePreference.objects.get(user=user)
print(f"Current layout: {pref.layout_mode}")
```

### Clear localStorage (if needed)
```javascript
localStorage.removeItem('minia-layout')
location.reload()
```

## Future Enhancements

1. **Animation Transitions**: Add CSS transitions when layout changes
2. **Keyboard Shortcut**: Add keyboard shortcut to quickly toggle layout
3. **User Preference Sync**: Sync preferences across multiple devices
4. **Layout History**: Track when user preferences change
5. **Bulk Reset**: Admin panel to reset all user preferences

## Completion Status

✅ **COMPLETE** - Layout persistence fully implemented and tested

**Deliverables:**
- ✅ Backend AJAX endpoint
- ✅ Database integration with UserThemePreference
- ✅ Frontend AJAX caller
- ✅ Page load restoration
- ✅ CSRF protection
- ✅ Error handling
- ✅ Console logging

**Session Summary:**
This completes the layout persistence feature. Users can now:
1. Select their preferred layout (vertical/horizontal)
2. Have it automatically saved to the database
3. See it restored on every page load and navigation
4. Confirm persistence persists across refresh and new sessions
