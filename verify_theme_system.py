#!/usr/bin/env python
"""
Comprehensive theme system verification script
Tests all aspects of the theme switching system
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

django.setup()

from accounting.models_theme import UserThemePreference, Theme
from django.contrib.auth.models import User
from django.test import Client
from django.template import Context, Template

print("=" * 70)
print("COMPREHENSIVE THEME SYSTEM VERIFICATION")
print("=" * 70)

# 1. Check database state
print("\n[1] DATABASE STATE")
print("-" * 70)
user = User.objects.get(username='zubair')
pref = UserThemePreference.objects.get(user=user)

print(f"User: {user.username}")
print(f"Current Theme: {pref.theme.name} ({pref.theme.display_name})")
print(f"Sidebar Color: {pref.sidebar_color}")
print(f"Layout Mode: {pref.layout_mode}")
print(f"Layout Size: {pref.layout_size}")

# 2. Check available themes
print("\n[2] AVAILABLE THEMES")
print("-" * 70)
for theme in Theme.objects.all():
    print(f"  ✓ {theme.name} - {theme.display_name}")

# 3. Verify context processor
print("\n[3] CONTEXT PROCESSOR")
print("-" * 70)
from accounting.context_processors import theme_context
from django.http import HttpRequest

request = HttpRequest()
request.user = user

context = theme_context(request)
print(f"  ✓ current_theme: {context['current_theme'].name if context.get('current_theme') else 'None'}")
print(f"  ✓ user_theme_pref: {context.get('user_theme_pref')}")
print(f"  ✓ available_themes: {len(context.get('available_themes', []))} themes")

# 4. Check template rendering
print("\n[4] TEMPLATE BODY TAG")
print("-" * 70)

template_str = '''<body data-bs-theme="{% if user_theme_pref.sidebar_color %}{{ user_theme_pref.sidebar_color }}{% else %}light{% endif %}" data-sidebar="{% if user_theme_pref.sidebar_color %}{{ user_theme_pref.sidebar_color }}{% else %}light{% endif %}" data-layout="{% if user_theme_pref.layout_mode %}{{ user_theme_pref.layout_mode }}{% else %}vertical{% endif %}" data-layout-size="{% if user_theme_pref.layout_size %}{{ user_theme_pref.layout_size }}{% else %}fluid{% endif %}" >'''

template = Template(template_str)
ctx = Context({
    'user_theme_pref': pref,
    'current_theme': pref.theme,
})
rendered = template.render(ctx)
print("Rendered HTML:")
print(rendered)

# 5. CSS Selector Check
print("\n[5] CSS SELECTORS THAT SHOULD APPLY")
print("-" * 70)
selectors = [
    f"body[data-bs-theme='{pref.sidebar_color}']",
    f"body[data-sidebar='{pref.sidebar_color}']",
    f"body[data-layout='{pref.layout_mode}']",
    f"body[data-layout-size='{pref.layout_size}']",
]
for selector in selectors:
    print(f"  ✓ {selector}")

# 6. Client test
print("\n[6] HTTP CLIENT TEST")
print("-" * 70)
client = Client()
client.force_login(user)

response = client.get('/accounting/dashboard/')
print(f"Status Code: {response.status_code}")
print(f"Content Type: {response.get('content-type')}")

# Check if body tag is in the response
if f'data-bs-theme="{pref.sidebar_color}"' in response.content.decode():
    print(f"✓ Body has data-bs-theme='{pref.sidebar_color}'")
else:
    print(f"✗ Body missing data-bs-theme='{pref.sidebar_color}'")

if f'data-sidebar="{pref.sidebar_color}"' in response.content.decode():
    print(f"✓ Body has data-sidebar='{pref.sidebar_color}'")
else:
    print(f"✗ Body missing data-sidebar='{pref.sidebar_color}'")

if f'data-layout-size="{pref.layout_size}"' in response.content.decode():
    print(f"✓ Body has data-layout-size='{pref.layout_size}'")
else:
    print(f"✗ Body missing data-layout-size='{pref.layout_size}'")

print("\n" + "=" * 70)
print("VERIFICATION COMPLETE")
print("=" * 70)
