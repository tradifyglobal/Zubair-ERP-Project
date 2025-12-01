# TradifyERP Theme Switching System

## Overview

The Theme Switching System allows users to dynamically switch between different themes (e.g., Minia, Starter Kit) while maintaining full functionality across all modules. Users can customize their experience without losing any data or module capabilities.

## Features

✅ **Theme Switching**
- Switch between multiple themes (Minia, Starter Kit, and custom themes)
- Changes applied instantly across all modules
- No data loss or module disruption

✅ **Layout Customization**
- Sidebar color options (Light/Dark)
- Layout modes (Vertical/Horizontal)
- Container width options (Fluid/Boxed)

✅ **Per-User Preferences**
- Each user has their own theme preference
- Auto-created when user is registered
- Saved to database for persistence

✅ **Module-Wide Support**
- Works with all TradifyERP modules:
  - Accounting
  - HR
  - CRM
  - Inventory
  - Procurement
  - Sales
  - Manufacturing
  - Projects
  - And more...

✅ **Admin Management**
- Django Admin interface to manage available themes
- Enable/disable themes for users
- View and modify user preferences

## Installation & Setup

### Step 1: Update Models
The theme models are defined in `accounting/models_theme.py`:
- `Theme` - Available themes in the system
- `UserThemePreference` - Per-user theme preferences

### Step 2: Create & Run Migration
```bash
# Create migration
python manage.py makemigrations

# Apply migration
python manage.py migrate
```

### Step 3: Register Admin
Add to `accounting/admin.py`:
```python
from accounting.admin_theme import ThemeAdmin, UserThemePreferenceAdmin
```

### Step 4: Update Settings
The theme context processor is already added to `TEMPLATES['OPTIONS']['context_processors']`:
```python
'accounting.context_processors.theme_context',
```

### Step 5: Add URLs
URLs are already added to `accounting/urls.py`:
```python
path('theme/', include('accounting.urls_theme')),
```

### Step 6: Load Initial Themes
Create a script or use Django shell to load themes:

```python
from accounting.models_theme import Theme

# Create default themes
themes_data = [
    {
        'name': 'minia',
        'display_name': 'Minia - Dark Professional',
        'description': 'Dark professional theme with modern design',
        'is_active': True,
    },
    {
        'name': 'starterkit',
        'display_name': 'Starter Kit - Light Clean',
        'description': 'Light clean theme for minimal interface',
        'is_active': True,
    },
]

for theme_data in themes_data:
    Theme.objects.get_or_create(
        name=theme_data['name'],
        defaults=theme_data
    )
```

## Usage

### User Dashboard Theme Switcher

1. **Access Theme Settings**
   - Navigate to: `/accounting/theme/settings/`
   - Or add link to dashboard: 
   ```html
   <a href="{% url 'accounting:theme:theme_settings' %}">Theme Settings</a>
   ```

2. **Switch Theme**
   - Click "Switch Theme" button on desired theme card
   - Page reloads with new theme applied
   - Success message confirms change

3. **Customize Layout**
   - Adjust sidebar color
   - Change layout mode
   - Set container width
   - Changes apply immediately

### Available URLs

```
GET  /accounting/theme/settings/           - Theme settings page
POST /accounting/theme/api/switch/         - Switch theme API
POST /accounting/theme/api/update-layout/  - Update layout settings API
GET  /accounting/theme/api/get-settings/   - Get current settings
GET  /accounting/theme/preview/<theme>/    - Preview theme
```

### JavaScript API

```javascript
// Switch theme
switchTheme('minia', buttonElement);

// Update layout setting
updateLayoutSetting('sidebar_color', 'dark', buttonElement);
updateLayoutSetting('layout_mode', 'horizontal', buttonElement);
updateLayoutSetting('layout_size', 'boxed', buttonElement);

// Get CSRF token
getCookie('csrftoken');
```

## Template Integration

### Available Template Variables

In any template, access theme information:

```html
<!-- Current theme -->
<p>{{ current_theme.name }}</p>
<p>{{ current_theme.display_name }}</p>

<!-- All available themes -->
{% for theme in available_themes %}
    <p>{{ theme.display_name }}</p>
{% endfor %}

<!-- User preferences -->
<p>{{ user_theme_pref.sidebar_color }}</p>
<p>{{ user_theme_pref.layout_mode }}</p>
<p>{{ user_theme_pref.layout_size }}</p>
```

### Dynamic Theme Assets

Use theme data to load appropriate stylesheets:

```html
<link href="{% static 'themes/' %}{{ current_theme.name }}/style.css" rel="stylesheet">
```

## Adding Custom Themes

### Step 1: Create Theme Directory
```
static/themes/
├── minia/
│   ├── css/
│   ├── js/
│   └── images/
├── starterkit/
│   ├── css/
│   ├── js/
│   └── images/
└── mytheme/
    ├── css/
    ├── js/
    └── images/
```

### Step 2: Add Theme to Database
```python
from accounting.models_theme import Theme

Theme.objects.create(
    name='mytheme',
    display_name='My Custom Theme',
    description='Custom theme for TradifyERP',
    is_active=True,
    thumbnail_url='/static/themes/mytheme/thumbnail.png'
)
```

### Step 3: Update Theme Choices
Update `models_theme.py`:
```python
THEME_CHOICES = [
    ('minia', 'Minia - Dark Professional'),
    ('starterkit', 'Starter Kit - Light Clean'),
    ('mytheme', 'My Custom Theme'),
]
```

## Data Persistence

✅ **Theme switching does NOT affect:**
- User data
- Module records (accounting entries, HR data, CRM contacts, etc.)
- Permissions
- Settings
- Any saved information

✅ **What IS saved:**
- User's selected theme
- Layout preferences
- Sidebar color
- Layout mode
- Container width setting

## Module Compatibility

The theme system works seamlessly with:

| Module | Status |
|--------|--------|
| Accounting | ✅ Fully Supported |
| HR | ✅ Fully Supported |
| CRM | ✅ Fully Supported |
| Inventory | ✅ Fully Supported |
| Procurement | ✅ Fully Supported |
| Sales | ✅ Fully Supported |
| Manufacturing | ✅ Fully Supported |
| Projects | ✅ Fully Supported |
| AP (Accounts Payable) | ✅ Fully Supported |
| AR (Accounts Receivable) | ✅ Fully Supported |
| Maintenance | ✅ Fully Supported |

## Admin Management

### Access Admin Interface
1. Go to Django Admin: `/admin/`
2. Navigate to "Accounting" → "Themes"
3. Manage available themes
4. View "User Theme Preferences"
5. Monitor user preferences

### Theme Administration Tasks

**Create New Theme:**
1. Click "Add Theme" in Admin
2. Fill in theme details:
   - Name (system identifier)
   - Display Name (user-friendly name)
   - Description
   - Activation status
   - Thumbnail URL

**Deactivate Theme:**
1. Select theme
2. Uncheck "Is Active"
3. Save
4. Theme won't appear in user selections

**View User Preferences:**
1. Go to "User Theme Preferences"
2. See which users use which themes
3. Edit individual preferences if needed

## Performance Considerations

✅ **Optimized Queries**
- UserThemePreference is retrieved via OneToOneField (efficient)
- Theme is ForeignKey (indexed)
- Database hits are minimal

✅ **Caching**
- Context processor caches theme per request
- No repeated database queries per page view

✅ **Static Files**
- Themes are separate static file sets
- Browser caches stylesheets
- Fast switching with minimal re-render

## Security & Permissions

✅ **Authentication Required**
- Theme switching only available to logged-in users
- All API endpoints require authentication

✅ **CSRF Protection**
- All POST requests require CSRF token
- Validated server-side

✅ **Data Isolation**
- Users can only modify their own preferences
- Admin has full access to manage all themes

## Troubleshooting

### Theme Not Switching
**Symptom:** Button click doesn't change theme

**Solution:**
1. Check browser console for errors
2. Verify CSRF token is present
3. Ensure migrations are applied
4. Check user permissions

### Theme Not Loading
**Symptom:** Theme appears but styles missing

**Solution:**
1. Verify static files are collected: `python manage.py collectstatic`
2. Check theme directory structure
3. Verify theme name matches database entry
4. Check CSS file paths

### User Preferences Not Saving
**Symptom:** Changes don't persist after reload

**Solution:**
1. Check database connection
2. Verify migration is applied
3. Check user has theme_preference record
4. Review server logs for errors

## API Reference

### Switch Theme

**Endpoint:** `POST /accounting/theme/api/switch/`

**Request:**
```json
{
    "theme_name": "minia"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Switched to Minia - Dark Professional",
    "theme_name": "minia",
    "redirect_url": "/accounting/dashboard/"
}
```

### Update Layout Settings

**Endpoint:** `POST /accounting/theme/api/update-layout/`

**Request:**
```json
{
    "sidebar_color": "dark",
    "layout_mode": "horizontal",
    "layout_size": "boxed"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Layout settings updated"
}
```

### Get Current Settings

**Endpoint:** `GET /accounting/theme/api/get-settings/`

**Response:**
```json
{
    "success": true,
    "theme": "minia",
    "sidebar_color": "light",
    "layout_mode": "vertical",
    "layout_size": "fluid"
}
```

## Future Enhancements

Possible improvements:
1. Theme color customization
2. Font selection options
3. Theme preview before switching
4. Bulk theme assignment to users
5. Theme scheduling (auto-switch at time)
6. Custom theme builder UI
7. Theme import/export functionality
8. Organization-wide theme settings

## Support

For issues or questions:
1. Check this documentation
2. Review Django Admin interface
3. Check database migration status
4. Review server logs
5. Test with admin user account

## File Structure

```
accounting/
├── models_theme.py           # Theme models
├── views_theme.py            # Theme views & APIs
├── urls_theme.py             # Theme URLs
├── context_processors.py      # Theme context (updated)
├── admin_theme.py            # Django admin
├── migrations/
│   └── 0014_theme_userthemepreference.py  # Migration
└── templates/accounting/
    └── theme_settings.html   # Settings page
```

## Version History

### v1.0 - Initial Release
- Basic theme switching (Minia, Starter Kit)
- Layout customization
- Per-user preferences
- Admin interface
- All modules supported
