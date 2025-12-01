# Theme Switching System - Quick Setup Guide

## Quick Start (5 Steps)

### Step 1: Run Migration
```bash
cd g:\TradifyERP\TradifyERP
python manage.py migrate
```

### Step 2: Create Initial Themes
```bash
python manage.py shell
```

Then paste this:
```python
from accounting.models_theme import Theme

# Create themes
themes_data = [
    {
        'name': 'minia',
        'display_name': 'Minia - Dark Professional',
        'description': 'Dark professional theme with modern design and comprehensive features',
        'is_active': True,
    },
    {
        'name': 'starterkit',
        'display_name': 'Starter Kit - Light Clean',
        'description': 'Light clean theme with minimalist design perfect for startups',
        'is_active': True,
    },
]

for theme_data in themes_data:
    obj, created = Theme.objects.get_or_create(
        name=theme_data['name'],
        defaults=theme_data
    )
    if created:
        print(f"✓ Created theme: {theme_data['display_name']}")
    else:
        print(f"✓ Theme already exists: {theme_data['display_name']}")

print("\nAll themes loaded!")
exit()
```

### Step 3: Add Dashboard Link
Edit `templates/dashboard.html` or `templates/partials/navbar.html` and add:

```html
<a href="{% url 'accounting:theme:theme_settings' %}" class="nav-link">
    🎨 Themes
</a>
```

Or add to user profile dropdown:
```html
<a class="dropdown-item" href="{% url 'accounting:theme:theme_settings' %}">
    <i class="mdi mdi-palette"></i> Theme Settings
</a>
```

### Step 4: Test Setup
1. Go to Django Admin: http://localhost:8000/admin/
2. Navigate to Accounting → Themes
3. Verify 2 themes are listed and active

### Step 5: Access Theme Switcher
1. Navigate to: `http://localhost:8000/accounting/theme/settings/`
2. Try switching themes
3. Try changing layout settings
4. Verify page reloads with new theme

## What Happens Next?

✅ Users can now:
- Switch between themes anytime from dashboard
- Customize layout (sidebar, layout mode, width)
- Settings persist across sessions
- All modules work with selected theme

✅ You can:
- Add more themes (see Full Documentation)
- Customize theme directories
- Extend with additional preferences
- Manage themes from Django Admin

## File Checklist

Make sure these files exist:
- ✅ `accounting/models_theme.py` - Models
- ✅ `accounting/views_theme.py` - Views
- ✅ `accounting/urls_theme.py` - URLs
- ✅ `accounting/admin_theme.py` - Admin
- ✅ `accounting/context_processors.py` - Updated with theme_context
- ✅ `accounting/migrations/0014_theme_userthemepreference.py` - Migration
- ✅ `accounting/templates/accounting/theme_settings.html` - UI
- ✅ `TradifyERP/settings.py` - Updated with context processor
- ✅ `accounting/urls.py` - Updated with theme URLs

## Integration Points

### In Templates
```html
<!-- Show current theme -->
Current Theme: {{ current_theme.display_name }}

<!-- List all themes -->
{% for theme in available_themes %}
    {{ theme.display_name }}
{% endfor %}

<!-- User preferences -->
Sidebar: {{ user_theme_pref.sidebar_color }}
Layout: {{ user_theme_pref.layout_mode }}
Size: {{ user_theme_pref.layout_size }}
```

### In Views
```python
from accounting.models_theme import UserThemePreference

# Get user's theme
pref = UserThemePreference.get_or_create_for_user(request.user)
print(pref.theme.name)  # 'minia'
print(pref.sidebar_color)  # 'light'
```

## Common Issues & Solutions

### Issue: Module Not Found Error
**Solution:** Make sure migration is applied: `python manage.py migrate`

### Issue: Settings Not Saving
**Solution:** Check database connection and migration status

### Issue: Theme Not Loading
**Solution:** Run `python manage.py collectstatic` to collect static files

### Issue: 404 on Theme URL
**Solution:** Verify theme URLs are included in `accounting/urls.py`

## Next Steps

1. **Add More Themes** - Follow adding custom themes section in full docs
2. **Customize UI** - Modify `theme_settings.html` for your branding
3. **Add Team Settings** - Store organization-wide theme preferences
4. **Auto-Switch** - Schedule automatic theme switching (dark mode at night)
5. **Theme Preview** - Let users preview before switching

## Full Documentation

See `THEME_SWITCHING_DOCUMENTATION.md` for:
- Complete API reference
- Adding custom themes
- Advanced customization
- Troubleshooting guide
- Performance optimization

## Testing Checklist

- [ ] Migration applied successfully
- [ ] Themes created in database
- [ ] Admin shows themes
- [ ] Dashboard link added
- [ ] Theme switcher page loads
- [ ] Can switch between themes
- [ ] Layout settings work
- [ ] Settings persist on page reload
- [ ] All modules work with each theme
- [ ] User data not affected by theme change

## Need Help?

1. Check `THEME_SWITCHING_DOCUMENTATION.md`
2. Review Django Admin for theme configuration
3. Test with admin account first
4. Check browser console for JavaScript errors
5. Review server logs for backend errors

---

**Status:** Ready to Use ✅
**Last Updated:** November 29, 2025
