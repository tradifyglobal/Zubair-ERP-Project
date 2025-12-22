#!/usr/bin/env python
"""Check if themes exist in production database."""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
sys.path.insert(0, '/var/www/tradifyerp/TradifyERP')
django.setup()

from accounting.models_theme import Theme, UserThemePreference
from django.contrib.auth.models import User

print("=== THEME CHECK ===")
print(f"Total themes: {Theme.objects.count()}")
for theme in Theme.objects.all():
    print(f"  - {theme.name}: {theme.display_name} (active={theme.is_active})")

print("\n=== USER THEME PREFERENCES ===")
print(f"Total user preferences: {UserThemePreference.objects.count()}")
user_count = User.objects.filter(is_active=True).count()
print(f"Total active users: {user_count}")
print(f"Users without preference: {user_count - UserThemePreference.objects.count()}")

# List first 5 user preferences
for pref in UserThemePreference.objects.all()[:5]:
    print(f"  - {pref.user.username}: {pref.theme.display_name} (layout={pref.layout_mode})")
