#!/usr/bin/env python
"""Check current theme and offer to switch."""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from accounting.models_theme import UserThemePreference, Theme
from django.contrib.auth.models import User

user = User.objects.get(username='zubair')
pref = UserThemePreference.objects.get(user=user)

print("=" * 60)
print("CURRENT THEME STATUS")
print("=" * 60)
print(f"\nUser: {user.username}")
print(f"Current Theme: {pref.theme.display_name}")
print(f"Sidebar: {pref.sidebar_color}")
print(f"Layout Mode: {pref.layout_mode}")
print(f"Layout Size: {pref.layout_size}")

print("\n" + "=" * 60)
print("To switch themes, go to:")
print("http://localhost:8000/accounting/theme/settings/")
print("\nOr switch programmatically by running:")
print("  python switch_to_minia.py (for Dark sidebar + Boxed layout)")
print("  python switch_to_starterkit.py (for Light sidebar + Fluid layout)")
print("=" * 60)
