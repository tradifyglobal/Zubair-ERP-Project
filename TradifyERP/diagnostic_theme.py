#!/usr/bin/env python
"""Diagnostic script to check theme rendering in actual HTML."""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from accounting.models_theme import UserThemePreference

# Login and fetch a page
client = Client()
user = User.objects.get(username='zubair')
client.force_login(user)

# Get dashboard page
response = client.get('/accounting/dashboard/', follow=True)

print("=" * 70)
print("THEME APPLICATION DIAGNOSTIC")
print("=" * 70)

print(f"\nResponse Status: {response.status_code}")
print(f"Content Length: {len(response.content)} bytes")

# Get the content
content = response.content.decode('utf-8')

# Find body tag
import re
body_match = re.search(r'<body[^>]*>', content)

if body_match:
    body_tag = body_match.group(0)
    print(f"\nBody Tag Found:")
    print(f"  {body_tag}")
    
    # Extract attributes
    sidebar_match = re.search(r'data-sidebar="([^"]*)"', body_tag)
    layout_match = re.search(r'data-layout="([^"]*)"', body_tag)
    size_match = re.search(r'data-layout-size="([^"]*)"', body_tag)
    
    if sidebar_match:
        print(f"\n✓ data-sidebar = \"{sidebar_match.group(1)}\"")
    else:
        print(f"\n✗ data-sidebar NOT found in body tag")
        
    if layout_match:
        print(f"✓ data-layout = \"{layout_match.group(1)}\"")
    else:
        print(f"✗ data-layout NOT found in body tag")
        
    if size_match:
        print(f"✓ data-layout-size = \"{size_match.group(1)}\"")
    else:
        print(f"✗ data-layout-size NOT found in body tag")
else:
    print("\n✗ Body tag NOT found in response!")
    print("\nFirst 2000 chars of response:")
    print(content[:2000])

# Check user preferences in database
pref = UserThemePreference.objects.get(user=user)
print(f"\n\nDatabase Theme Preferences for '{user.username}':")
print(f"  - Theme: {pref.theme.display_name}")
print(f"  - Sidebar Color: {pref.sidebar_color}")
print(f"  - Layout Mode: {pref.layout_mode}")
print(f"  - Layout Size: {pref.layout_size}")

print("\n" + "=" * 70)
if sidebar_match and layout_match and size_match:
    print("✓ THEME IS PROPERLY APPLIED IN HTML")
    print("\nExpected Visual Changes:")
    if sidebar_match.group(1) == 'dark':
        print("  - Sidebar should be DARK")
    elif sidebar_match.group(1) == 'light':
        print("  - Sidebar should be LIGHT")
    
    if size_match.group(1) == 'boxed':
        print("  - Layout should be BOXED (centered with margins)")
    elif size_match.group(1) == 'fluid':
        print("  - Layout should be FLUID (full width)")
else:
    print("✗ THEME IS NOT BEING APPLIED - CHECK TEMPLATE")

print("=" * 70)
