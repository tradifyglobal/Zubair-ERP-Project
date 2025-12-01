# Theme Switching System - Visual Overview

## 🎨 System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    TradifyERP Dashboard                          │
│  [🎨 Theme Settings Link] ← User clicks here                    │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│              Theme Settings Page (/theme/settings/)              │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ Available Themes:                                          │ │
│  │ ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │ │
│  │ │   Minia      │  │ Starter Kit  │  │  Custom...   │     │ │
│  │ │   (Dark)     │  │   (Light)    │  │  (if added)  │     │ │
│  │ │              │  │              │  │              │     │ │
│  │ │ [Switch]     │  │ [Switch]     │  │ [Switch]     │     │ │
│  │ └──────────────┘  └──────────────┘  └──────────────┘     │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ Layout Settings:                                           │ │
│  │ Sidebar: [☀️ Light] [🌙 Dark]                             │ │
│  │ Layout:  [📊 Vertical] [↔️ Horizontal]                    │ │
│  │ Width:   [📱 Fluid] [📦 Boxed]                            │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                       │
              User clicks [Switch Theme]
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│              Theme Switch API Endpoint                           │
│        POST /accounting/theme/api/switch/                       │
│                                                                  │
│  Request: { "theme_name": "minia" }                            │
│                                                                  │
│  ✓ Validate theme exists                                       │
│  ✓ Validate theme is active                                    │
│  ✓ Update UserThemePreference                                  │
│  ✓ Save to database                                            │
│                                                                  │
│  Response: { "success": true, ... }                            │
└──────────────────────┬──────────────────────────────────────────┘
                       │
              JavaScript reloads page
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Page Request (HTTP GET)                        │
│                   /accounting/dashboard/                        │
│                                                                  │
│  ✓ context_processors.theme_context() called                   │
│  ✓ Retrieves UserThemePreference from database                │
│  ✓ Retrieves current Theme from database                       │
│  ✓ Adds to template context:                                  │
│    - {{ current_theme }}                                       │
│    - {{ user_theme_pref }}                                     │
│    - {{ available_themes }}                                    │
└──────────────────────┬──────────────────────────────────────────┘
                       │
              Template renders with theme
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│              Dashboard with New Theme                            │
│         (All modules work - no data affected)                   │
│                                                                  │
│  ✓ Sidebar styled with new theme                              │
│  ✓ Navigation themed                                           │
│  ✓ All controls work                                           │
│  ✓ Data intact and accessible                                 │
│  ✓ All modules functional                                     │
│                                                                  │
│  Accounting, HR, CRM, Inventory, etc. - all working! ✅        │
└─────────────────────────────────────────────────────────────────┘
```

## 📊 Data Model Relationships

```
┌──────────────────────────┐
│    auth_user             │
│ (Django User Model)      │
│                          │
│  id (PK)                 │
│  username                │
│  email                   │
│  ...                     │
└────────┬─────────────────┘
         │
         │ (OneToOneField)
         │
         │ Signal: auto-create on user create
         │
         ▼
┌──────────────────────────────────────────┐
│  user_theme_preference                   │
│  (User's Theme Settings)                 │
│                                          │
│  id (PK)                                 │
│  user_id (FK to auth_user)               │◄──── Unique per user
│  theme_id (FK to theme)                  │
│  sidebar_color (light/dark)              │
│  layout_mode (vertical/horizontal)       │
│  layout_size (fluid/boxed)               │
│  created_at                              │
│  updated_at                              │
└────────┬─────────────────────────────────┘
         │
         │ (ForeignKey PROTECT)
         │
         ▼
┌──────────────────────────┐
│    theme                 │
│  (Available Themes)      │
│                          │
│  id (PK)                 │
│  name (unique)           │
│  display_name            │
│  description             │
│  is_active (bool)        │
│  thumbnail_url           │
│  created_at              │
│  updated_at              │
└──────────────────────────┘
```

## 🔄 Theme Switching Workflow

```
User Login
   │
   ▼
Signal: post_save on User
   │
   ├─ Check if user already has theme_preference
   │
   ├─ If no ─► Create UserThemePreference with default theme (minia)
   │
   └─ If yes ─► Use existing preference
        │
        ▼
    User logged in with their theme


User Navigates Dashboard
   │
   ▼
Request: GET /dashboard/
   │
   ▼
Django processes request
   │
   ├─ context_processors.theme_context() executes
   │   │
   │   ├─ Check if user is authenticated
   │   │
   │   ├─ Get available themes from database
   │   │
   │   ├─ Get user's theme preference
   │   │
   │   └─ Add to context:
   │       - current_theme
   │       - user_theme_pref
   │       - available_themes
   │
   ▼
Template renders with theme context
   │
   ├─ Load theme-specific CSS: /static/themes/{{ current_theme.name }}/
   │
   ├─ Apply layout settings:
   │   - Sidebar color: data-sidebar="{{ user_theme_pref.sidebar_color }}"
   │   - Layout mode: data-layout="{{ user_theme_pref.layout_mode }}"
   │   - Layout size: data-layout-size="{{ user_theme_pref.layout_size }}"
   │
   └─ Render page with new theme
        │
        ▼
    User sees dashboard with their theme


User Clicks "Switch Theme"
   │
   ▼
JavaScript: switchTheme('new_theme')
   │
   ├─ Disable button (prevent double-click)
   │
   ├─ Get CSRF token from cookie
   │
   └─ Send AJAX POST:
       POST /accounting/theme/api/switch/
       { "theme_name": "starterkit" }
        │
        ▼
    View: switch_theme()
        │
        ├─ Validate theme exists
        │
        ├─ Validate theme is active
        │
        ├─ Get UserThemePreference
        │   (or create if doesn't exist)
        │
        ├─ Update preference.theme
        │
        ├─ Save to database
        │
        └─ Return JSON:
           { "success": true, ... }
              │
              ▼
    JavaScript receives response
        │
        ├─ Update UI (show success message)
        │
        ├─ Update button text
        │
        ├─ Mark theme as active
        │
        └─ Reload page: location.reload()
           │
           ▼
       Entire cycle repeats ─────┐
                                 │
                                 └─ New theme displays!
```

## 📁 File Structure

```
TradifyERP/
├── TradifyERP/
│   └── settings.py                    (UPDATED - added theme context processor)
│
├── accounting/
│   ├── models_theme.py                (NEW - Theme models)
│   │   ├── Theme
│   │   └── UserThemePreference
│   │
│   ├── views_theme.py                 (NEW - Theme views)
│   │   ├── theme_list()
│   │   ├── switch_theme()
│   │   ├── update_layout_settings()
│   │   ├── get_user_theme_settings()
│   │   └── ThemePreviewView
│   │
│   ├── urls_theme.py                  (NEW - Theme URLs)
│   │   ├── settings/
│   │   ├── api/switch/
│   │   ├── api/update-layout/
│   │   ├── api/get-settings/
│   │   └── preview/<theme>/
│   │
│   ├── urls.py                        (UPDATED - included theme URLs)
│   │
│   ├── admin_theme.py                 (NEW - Admin classes)
│   │   ├── ThemeAdmin
│   │   └── UserThemePreferenceAdmin
│   │
│   ├── context_processors.py          (UPDATED - added theme_context())
│   │
│   ├── migrations/
│   │   └── 0014_theme_userthemepreference.py  (NEW - Migration)
│   │
│   └── templates/accounting/
│       └── theme_settings.html        (NEW - Theme UI)
│
└── Documentation/
    ├── THEME_IMPLEMENTATION_SUMMARY.md
    ├── THEME_SWITCHING_DOCUMENTATION.md
    ├── THEME_SETUP_QUICK_START.md
    ├── THEME_USER_GUIDE.md
    └── THEME_SYSTEM_CHECKLIST.md
```

## 🎯 User Journey

```
┌─────────────────────────────────────────────────────────┐
│  First Time User                                         │
│                                                         │
│  1. Register/Login                                      │
│     ↓                                                   │
│  2. System creates default theme preference (Minia)    │
│     ↓                                                   │
│  3. Dashboard loads with Minia theme                   │
│     ↓                                                   │
│  4. User sees "🎨 Theme Settings" in navigation        │
│     ↓                                                   │
│  5. Clicks link → goes to theme settings page          │
│     ↓                                                   │
│  6. Sees available themes                              │
│     ↓                                                   │
│  7. Reads descriptions and customizes layout           │
│     ↓                                                   │
│  8. Switches to preferred theme                        │
│     ↓                                                   │
│  9. All modules load with new theme                    │
│     ↓                                                   │
│ 10. Settings saved - same theme on next login         │
│                                                         │
└─────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────┐
│  Existing User                                           │
│                                                         │
│  1. Login with existing account                        │
│     ↓                                                   │
│  2. System retrieves saved theme preference            │
│     ↓                                                   │
│  3. Dashboard loads with previous theme               │
│     ↓                                                   │
│  4. User can:                                          │
│     • Keep current theme                              │
│     • Switch to different theme                       │
│     • Adjust layout settings                          │
│     ↓                                                   │
│  5. Any changes saved automatically                    │
│     ↓                                                   │
│  6. Settings preserved on next login                  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## 💾 Data Flow Diagram

```
Request comes in
        │
        ▼
Django middleware processes
        │
        ▼
Request reaches view
        │
        ├─ For theme list:
        │  │
        │  ├─ Check authentication ✓
        │  │
        │  ├─ Query available themes
        │  │     Theme.objects.filter(is_active=True)
        │  │
        │  ├─ Query user preference
        │  │     UserThemePreference.objects.get(user=request.user)
        │  │
        │  └─ Render template with context
        │
        ├─ For theme switch:
        │  │
        │  ├─ Parse JSON request body
        │  │
        │  ├─ Validate theme exists
        │  │     Theme.objects.get(name=theme_name, is_active=True)
        │  │
        │  ├─ Update user preference
        │  │     pref.theme = theme
        │  │     pref.save()
        │  │
        │  └─ Return JSON response
        │
        ├─ For layout update:
        │  │
        │  ├─ Parse request
        │  │
        │  ├─ Get user preference
        │  │
        │  ├─ Update fields
        │  │
        │  ├─ Save to DB
        │  │
        │  └─ Return JSON response
        │
        └─ For dashboard (normal page):
           │
           ├─ context_processors.theme_context() called
           │  │
           │  ├─ Check user authentication
           │  │
           │  ├─ Query available themes
           │  │
           │  ├─ Query user preference
           │  │
           │  └─ Add to context dict
           │
           ├─ Template renders
           │  │
           │  ├─ Uses {{ current_theme }}
           │  │
           │  ├─ Uses {{ user_theme_pref }}
           │  │
           │  ├─ Uses {{ available_themes }}
           │  │
           │  └─ Generates HTML with theme styles
           │
           └─ Response sent to user
```

## 🔐 Security Layers

```
Request → Theme Endpoint
    │
    ▼
Layer 1: Authentication
    │
    ├─ Check if user is logged in
    │
    └─ Redirect to login if not authenticated
        │
        ▼
Layer 2: CSRF Protection
    │
    ├─ For POST requests:
    │   - Check CSRF token in request
    │   - Compare with session CSRF
    │   - Reject if missing or invalid
    │
    └─ Continue if valid
        │
        ▼
Layer 3: Input Validation
    │
    ├─ Validate theme_name format
    │
    ├─ Verify theme exists in database
    │
    ├─ Check theme is_active flag
    │
    └─ Reject if any validation fails
        │
        ▼
Layer 4: Authorization
    │
    ├─ Verify user can only modify own preferences
    │
    └─ Allow admin to modify any preference
        │
        ▼
Layer 5: SQL Injection Prevention
    │
    ├─ Use Django ORM (no raw SQL)
    │
    ├─ Use parameterized queries
    │
    └─ Automatic escaping by Django
        │
        ▼
Layer 6: XSS Prevention
    │
    ├─ Template escaping (default)
    │
    ├─ JSON encoding for API
    │
    └─ Sanitized output
        │
        ▼
Process validated, safe request
        │
        ▼
Update database
        │
        ▼
Return response
```

## 📈 Performance Optimization

```
Request received
        │
        ▼
Check cache
        │
        ├─ Context processor cached per request ✓
        │
        └─ DB queries minimized ✓
        │
        ▼
Execute query
        │
        ├─ OneToOneField optimized
        │   └─ Single query for user preference
        │
        ├─ ForeignKey indexed
        │   └─ Single query for theme
        │
        └─ Total: 1-2 queries max
        │
        ▼
Render template
        │
        ├─ Uses cached theme data
        │
        ├─ CSS file served from static
        │   └─ Browser cached
        │
        └─ Lightning fast
        │
        ▼
Send response (~100ms)
```

## 🎨 Theme Application

```
User has theme: minia

Static Files:
├── static/themes/minia/
│   ├── css/
│   │   ├── app.min.css
│   │   ├── bootstrap.min.css
│   │   └── theme-overrides.css
│   │
│   ├── js/
│   │   └── theme.js
│   │
│   └── images/
│       ├── logo.png
│       └── backgrounds/

HTML Template:
└─ <link href="/static/themes/minia/css/app.min.css">
   <body data-sidebar="{{ sidebar_color }}" 
         data-layout="{{ layout_mode }}"
         data-layout-size="{{ layout_size }}">


Result:
├─ Dark professional theme applied ✓
├─ Sidebar colored appropriately ✓
├─ Layout mode set correctly ✓
├─ Container sized properly ✓
└─ All modules use same theme ✓
```

---

**Visual Documentation Complete** ✅
**Last Updated:** November 29, 2025
